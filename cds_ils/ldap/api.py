# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS ldap API."""

import json
import time
import uuid
from functools import partial

from flask import current_app
from invenio_app_ils.errors import AnonymizationActiveLoansError
from invenio_app_ils.patrons.anonymization import anonymize_patron_data
from invenio_app_ils.patrons.indexer import PatronBaseIndexer
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount
from sqlalchemy.orm.exc import NoResultFound

from cds_ils.ldap.client import LdapClient
from cds_ils.ldap.user_importer import LdapUserImporter
from cds_ils.ldap.utils import InvenioUser, serialize_ldap_user, user_exists
from cds_ils.notifications.api import (
    UserDeletionWarningActiveLoanMessage,
    send_not_logged_notification,
)


def import_users():
    """Import LDAP users in db."""
    start_time = time.time()

    ldap_client = LdapClient()
    ldap_users = ldap_client.get_primary_accounts()

    print("Users in LDAP: {}".format(len(ldap_users)))

    imported = 0
    importer = LdapUserImporter()
    for ldap_user_data in ldap_users:
        ldap_user = serialize_ldap_user(ldap_user_data)
        already_exists = user_exists(ldap_user)

        if not ldap_user or already_exists:
            continue

        employee_id = ldap_user["remote_account_person_id"]
        print("Importing user with person id {}".format(employee_id))
        importer.import_user(ldap_user)
        imported += 1

    db.session.commit()

    print("Users imported: {}".format(imported))
    print("Now re-indexing all patrons...")

    current_app_ils.patron_indexer.reindex_patrons()

    print("--- Finished in %s seconds ---" % (time.time() - start_time))


def _log_info(log_uuid, action, extra=dict(), is_error=False):
    name = "ldap_users_synchronization"
    structured_msg = dict(name=name, uuid=log_uuid, action=action, **extra)
    structured_msg_str = json.dumps(structured_msg, sort_keys=True)
    if is_error:
        current_app.logger.error(structured_msg_str)
    else:
        current_app.logger.info(structured_msg_str)


def remap_invenio_users(log_func):
    """Create and return a list of all Invenio users."""
    invenio_remote_accounts_list = []
    remote_accounts = RemoteAccount.query.all()

    log_func("invenio_users_fetched", dict(users_fetched=len(remote_accounts)))

    # get all Invenio remote accounts and prepare a list with needed info
    for remote_account in remote_accounts:
        invenio_remote_accounts_list.append(remote_account)
    log_func("invenio_users_cached")
    return invenio_remote_accounts_list


def get_ldap_users(log_func):
    """Create and return a map of all LDAP users."""
    ldap_users_emails = set()
    ldap_users_map = {}

    # get all CERN users from LDAP
    ldap_client = LdapClient()
    ldap_users = ldap_client.get_primary_accounts()
    ldap_users_count = len(ldap_users)

    log_func("ldap_users_fetched", dict(users_fetched=ldap_users_count))

    for ldap_user_data in ldap_users:
        ldap_user = serialize_ldap_user(ldap_user_data, log_func=log_func)

        if ldap_user and ldap_user["user_email"] not in ldap_users_emails:
            ldap_person_id = ldap_user["remote_account_person_id"]
            ldap_users_map[ldap_person_id] = ldap_user
            ldap_users_emails.add(ldap_user["user_email"])

    log_func("ldap_users_cached")
    return ldap_users_count, ldap_users_map, ldap_users_emails


def update_users():
    """Sync LDAP users with local users in the DB."""

    def update_invenio_users_from_ldap(remote_accounts, ldap_users_map, log_func):
        """Iterate on all Invenio users to update outdated info from LDAP."""
        updated_count = 0

        # Note: cannot iterate on the db query here, because when a user is
        # deleted, db session will expire, causing a DetachedInstanceError when
        # fetching the user on the next iteration
        for remote_account in remote_accounts:
            invenio_user = InvenioUser(remote_account)
            # use `dict.pop` to remove from `ldap_users_map` the users found
            # in Invenio, so the remaining will be the ones to be added
            # later on
            ldap_user = ldap_users_map.pop(
                invenio_user.data["remote_account_person_id"], None
            )
            if not ldap_user:
                continue

            invenio_user.data.pop("remote_account_id")
            ldap_user.pop("cern_account_type")

            has_changed = invenio_user.data != ldap_user

            if has_changed:
                invenio_user.update(ldap_user)
                db.session.commit()
                log_func(
                    "user_updated",
                    dict(
                        user_id=invenio_user.user_id,
                        previous_department=invenio_user.data[
                            "remote_account_department"
                        ],
                        new_department=ldap_user["remote_account_department"],
                    ),
                )

                # re-index modified patron
                patron_indexer.index(patron_cls(invenio_user.user_id))

                updated_count += 1

        db.session.commit()
        log_func("invenio_users_updated_from_ldap", dict(count=updated_count))

        return ldap_users_map, updated_count

    def import_new_ldap_users(new_ldap_users, log_func):
        """Import any new LDAP user not in Invenio yet."""
        importer = LdapUserImporter()
        added_count = 0
        for ldap_user in new_ldap_users:
            # Check if email already exists in Invenio.
            # Apparently, in some cases, there could be multiple LDAP users
            # with different person id but same email.
            if not ldap_user:
                continue
            if user_exists(ldap_user):
                log_func(
                    "ldap_user_skipped_user_exists",
                    dict(
                        email=ldap_user["user_email"],
                        person_id=ldap_user["remote_account_person_id"],
                    ),
                )
                continue
            email = ldap_user["user_email"]
            employee_id = ldap_user["remote_account_person_id"]

            user_id = importer.import_user(ldap_user)
            log_func(
                "invenio_user_added",
                dict(email=email, employee_id=employee_id),
            )

            # index newly added patron
            patron_indexer.index(patron_cls(user_id))

            added_count += 1

        db.session.commit()
        log_func("import_new_users_done", dict(count=added_count))

        return added_count

    log_uuid = str(uuid.uuid4())
    log_func = partial(_log_info, log_uuid)
    start_time = time.time()

    patron_cls = current_app_ils.patron_cls
    patron_indexer = PatronBaseIndexer()

    ldap_users_count, ldap_users_map, ldap_users_emails = get_ldap_users(log_func)

    if not ldap_users_emails:
        return 0, 0, 0

    remote_acounts = remap_invenio_users(log_func)

    # STEP 1 - update Invenio users with info from LDAP
    ldap_users_map, invenio_users_updated = update_invenio_users_from_ldap(
        remote_acounts, ldap_users_map, log_func
    )

    # STEP 2 - import any new LDAP user not in Invenio yet
    invenio_users_added = 0
    new_ldap_users = ldap_users_map.values()

    if new_ldap_users:
        invenio_users_added = import_new_ldap_users(new_ldap_users, log_func)

    total_time = time.time() - start_time

    log_func("task_completed", dict(time=total_time))

    return (
        ldap_users_count,
        invenio_users_updated,
        invenio_users_added,
    )


def delete_users(dry_run=True, mark_for_deletion=True):
    """Delete users that are still in the DB but not in LDAP."""

    def _delete_user(user_id, invenio_user, dry_run=True, mark_for_deletion=True):
        ready_to_delete = True
        config_checks_before_deletion = current_app.config[
            "CDS_ILS_PATRON_DELETION_CHECKS"
        ]

        if mark_for_deletion:
            ready_to_delete = False
            checks = invenio_user.mark_for_deletion()
            if checks > config_checks_before_deletion:
                ready_to_delete = True

        if not dry_run and ready_to_delete:
            anonymize_patron_data(user_id)

        elif not dry_run and not ready_to_delete:
            return False
        return True

    users_deleted_count = 0
    users_ids_cannot_be_deleted = set()

    log_uuid = str(uuid.uuid4())
    log_func = partial(_log_info, log_uuid)

    ldap_users_count, ldap_users_map, _ = get_ldap_users(log_func)

    # get all Invenio remote accounts and prepare a list with needed info
    remote_accounts = remap_invenio_users(log_func)

    for remote_account in remote_accounts:
        try:
            invenio_user = InvenioUser(remote_account)
        except NoResultFound:
            continue
        ldap_user = ldap_users_map.get(invenio_user.data["remote_account_person_id"])

        if not ldap_user:
            # the user in Invenio does not exist in LDAP, delete it
            user_id = remote_account.user_id
            try:
                if _delete_user(user_id, invenio_user, dry_run, mark_for_deletion):
                    users_deleted_count += 1
            except AnonymizationActiveLoansError:
                users_ids_cannot_be_deleted.add(user_id)
        else:
            # user still in LDAP (or re-appeared)
            invenio_user.unmark_for_deletion()

    if not dry_run:
        current_app_ils.patron_indexer.reindex_patrons()

    if len(users_ids_cannot_be_deleted) > 0:
        send_alarm_patron_cannot_be_deleted(users_ids_cannot_be_deleted)

    return ldap_users_count, users_deleted_count


def send_alarm_patron_cannot_be_deleted(patron_pids):
    """Notify librarians that some users cannot be deleted.

    :param patron_pids: the pid of the patron.
    """
    patrons = []
    Patron = current_app_ils.patron_cls
    for patron_pid in patron_pids:
        patrons.append(Patron.get_patron(patron_pid))

    recipients = [
        {"email": recipient}
        for recipient in current_app.config["ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS"]
    ]
    msg = UserDeletionWarningActiveLoanMessage(patrons, recipients=recipients)
    send_not_logged_notification(recipients, msg)
