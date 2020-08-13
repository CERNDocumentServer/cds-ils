# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Books ldap API."""
import json
import uuid

import ldap
from flask import current_app
from invenio_accounts.models import User
from invenio_app_ils.anonymization import anonymize_patron_data
from invenio_app_ils.circulation.tasks import send_active_loans_mail
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile
from sqlalchemy.orm.exc import NoResultFound


class LdapClient(object):
    """Ldap client class for user importation/synchronization.

    Response example:
        [
            {'displayName': [b'Joe Foe'],
             'department': [b'IT/CDA'],
             'uidNumber': [b'100000'],
             'mail': [b'joe.foe@cern.ch'],
             'cernAccountType': [b'Primary'],
             'employeeID': [b'101010']
            },...
        ]
    """

    LDAP_USER_RESP_FIELDS = [
        "mail",
        "displayName",
        "department",
        "cernAccountType",
        "employeeID",
        "uidNumber",
    ]

    def __init__(self, ldap_url):
        """Initialize ldap connection."""
        self.ldap = ldap.initialize(ldap_url)

    def get_primary_accounts(self):
        """Retrieve all primary accounts from ldap."""
        page_control = ldap.controls.SimplePagedResultsControl(
            True, size=1000, cookie=""
        )

        response = self.ldap.search_ext(
            "OU=Users,OU=Organic Units,DC=cern,DC=ch",
            ldap.SCOPE_ONELEVEL,
            "(&(cernAccountType=Primary))",
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[page_control],
        )

        result = []
        pages = 0
        while True:
            pages += 1
            rtype, rdata, rmsgid, serverctrls = self.ldap.result3(response)
            result.extend([x[1] for x in rdata])
            ldap_page_control = ldap.controls.SimplePagedResultsControl
            ldap_page_control_type = ldap_page_control.controlType
            controls = [
                control
                for control in serverctrls
                if control.controlType == ldap_page_control_type
            ]
            if not controls:
                print("The server ignores RFC 2696 control")
                break
            if not controls[0].cookie:
                break
            page_control.cookie = controls[0].cookie
            response = self.ldap.search_ext(
                "OU=Users,OU=Organic Units,DC=cern,DC=ch",
                ldap.SCOPE_ONELEVEL,
                "(&(cernAccountType=Primary))",
                self.LDAP_USER_RESP_FIELDS,
                serverctrls=[page_control],
            )
        return result

    def get_user_by_person_id(self, person_id):
        """Query ldap to retrieve user by person id."""
        self.ldap.search_ext(
            "OU=Users,OU=Organic Units,DC=cern,DC=ch",
            ldap.SCOPE_ONELEVEL,
            "(&(cernAccountType=Primary)(employeeID={}))".format(person_id),
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[
                ldap.controls.SimplePagedResultsControl(
                    True, size=7, cookie=""
                )
            ],
        )

        res = self.ldap.result()[1]

        return [x[1] for x in res]

    def get_user_by_mail(self, mail):
        """Query ldap to retrieve user by person id."""
        self.ldap.search_ext(
            "OU=Users,OU=Organic Units,DC=cern,DC=ch",
            ldap.SCOPE_ONELEVEL,
            "(&(cernAccountType=Primary)(mail={}))".format(mail),
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[
                ldap.controls.SimplePagedResultsControl(
                    True, size=7, cookie=""
                )
            ],
        )

        res = self.ldap.result()[1]

        return [x[1] for x in res]


class LdapUserImporter:
    """Import ldap users to Invenio ILS records.

    Expected input format for ldap users:
        [
            {'displayName': [b'Joe Foe'],
             'department': [b'IT/CDA'],
             'uidNumber': [b'100000'],
             'mail': [b'joe.foe@cern.ch'],
             'cernAccountType': [b'Primary'],
             'employeeID': [b'101010']
            },...
        ]
    """

    def __init__(self, ldap_users):
        """Constructor."""
        self.ldap_users = ldap_users

    def import_user_identity(self, user_id, ldap_user):
        """Return new user identity entry."""
        return {
            "id": ldap_user["uidNumber"][0].decode("utf8"),
            "method": "cern",
            "id_user": user_id,
        }

    def import_user(self, user):
        """Return new user entry."""
        return {
            "email": user["mail"][0].decode("utf8"),
            "active": True,
        }

    def import_remote_account(self, user_id, ldap_user):
        """Return new user entry."""
        return {
            "user_id": user_id,
            "extra_data": {
                "person_id": ldap_user["employeeID"][0].decode("utf8"),
                "department": ldap_user["department"][0].decode("utf8"),
            },
        }

    def import_user_profile(self, user_id, ldap_user):
        """Return new user profile."""
        return {
            "user_id": user_id,
            "_displayname": "id_" + str(user_id),
            "full_name": ldap_user["displayName"][0].decode("utf8"),
        }

    def import_users(self):
        """Return location and internal location records."""

        def _commit_user(user_data):
            """Commit new user in db."""
            user = User(**self.import_user(user_data))
            db.session.add(user)
            db.session.commit()
            return user.id

        for ldap_user in self.ldap_users:
            print(
                "Importing user with person id {}".format(
                    ldap_user["employeeID"][0].decode("utf8")
                )
            )

            user_id = _commit_user(ldap_user)
            identity = UserIdentity(
                **self.import_user_identity(user_id, ldap_user)
            )
            db.session.add(identity)

            profile = UserProfile(
                **self.import_user_profile(user_id, ldap_user)
            )
            db.session.add(profile)

            client_id = (
                current_app.config.get("CERN_APP_CREDENTIALS", {}).get(
                    "consumer_key"
                ) or "CLIENT_ID"
            )
            remote_account = RemoteAccount(
                client_id=client_id,
                **self.import_remote_account(user_id, ldap_user)
            )
            db.session.add(remote_account)

        db.session.commit()


def import_ldap_users(ldap_users):
    """Import ldap users in db."""
    def index_ldap_users():
        """Index ldap users in ES."""
        from invenio_base.app import create_cli

        cli = create_cli()
        runner = current_app.test_cli_runner()
        command = "ils patrons index"
        runner.invoke(cli, command, catch_exceptions=True)
        _log_info("command_executed", dict(command=command))

    importer = LdapUserImporter(ldap_users)
    importer.import_users()
    index_ldap_users()
    _log_info("users_indexed")


def check_user_for_update(system_user, ldap_user):
    """Check if there is an ldap update for a user and commit changes."""
    ldap_user_department = ldap_user["department"][0].decode("utf8")
    if not system_user.extra_data["department"] == ldap_user_department:
        previous_department = system_user.extra_data["department"]

        system_user.extra_data.update(dict(department=ldap_user_department))
        db.session.commit()

        _log_info("department_updated",
                  dict(
                      user_id=system_user.user.id,
                      previous_department=previous_department,
                      new_department=ldap_user_department
                  ))


def delete_user(system_user):
    """Delete a system user."""
    with current_app.app_context():
        try:
            anonymize_patron_data(system_user.id)
        except AssertionError:
            send_active_loans_mail(system_user.id)


def _log_info(action, extra=None):
    if extra is None:
        extra = dict()
    name = "ldap_users_synchronization"
    structured_msg = dict(
        name=name,
        uuid=str(uuid.uuid4()),
        action=action,
        **extra,
    )
    structured_msg_str = json.dumps(structured_msg, sort_keys=True)
    current_app.logger.info(structured_msg_str)


def sync_users():
    """Sync ldap with system users command."""
    import time
    start_time = time.time()

    ldap_url = current_app.config["CDS_BOOKS_LDAP_URL"]
    ldap_client = LdapClient(ldap_url)
    system_users = RemoteAccount.query.join(User).all()
    ldap_users = ldap_client.get_primary_accounts()

    _log_info("users_fetched", dict(users_fetched=len(ldap_users)))

    ldap_users_map = {}

    system_users_updated_count = 0
    system_users_deleted_count = 0
    system_users_added_count = 0

    for ldap_user in ldap_users:
        ldap_person_id = ldap_user["employeeID"][0].decode("utf8")
        ldap_users_map.update({ldap_person_id: ldap_user})

    for system_user in system_users:
        system_user_person_id = system_user.extra_data["person_id"]
        ldap_user = ldap_users_map.get(system_user_person_id)
        if ldap_user:
            check_user_for_update(system_user, ldap_user)
        else:
            system_user_id = system_user.user
            delete_user(system_user)

            _log_info("user_deleted", dict(user_id=system_user_id))

    # Check if any ldap user is not in our system

    for ldap_user in ldap_users:
        ldap_mail = ldap_user["mail"][0].decode("utf8")
        try:
            User.query.filter(User.email == ldap_mail).one()
        except NoResultFound:
            import_ldap_users([ldap_user])
            _log_info("user_added", dict(ldap_mail=ldap_mail))
            system_users_added_count += 1

    total_time = time.time() - start_time

    _log_info("task_completed", dict(time=total_time))

    return (
        len(ldap_users),
        system_users_updated_count,
        system_users_deleted_count,
        system_users_added_count,
    )
