# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test LDAP functions."""

from copy import deepcopy

import pytest
from invenio_accounts.models import User
from invenio_app_ils.patrons.indexer import reindex_patrons
from invenio_app_ils.patrons.search import PatronsSearch
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_search import current_search
from invenio_userprofiles.models import UserProfile

from cds_ils.config import OAUTH_REMOTE_APP_NAME
from cds_ils.ldap.api import LdapUserImporter, _delete_invenio_user, \
    import_users, ldap_user_get, update_users
from cds_ils.ldap.models import Agent, LdapSynchronizationLog, TaskStatus


def test_send_email_delete_user_with_loans(app, patron1, testdata):
    """Test that email sent when the user is deleted with active loans."""
    with app.extensions["mail"].record_messages() as outbox:
        assert len(outbox) == 0
        _delete_invenio_user(patron1.id)
        assert len(outbox) == 1
        email = outbox[0]
        assert (
            email.recipients
            == app.config["ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS"]
        )

        def assert_contains(string):
            assert string in email.body
            assert string in email.html

        assert_contains("patron1@cern.ch")
        assert_contains("loanid-2")
        assert_contains(
            "Prairie Fires: The American Dreams of Laura Ingalls" " Wilder"
        )


def test_import_users(app, db, testdata, mocker):
    """Test import of users from LDAP."""
    ldap_users = [
        {
            "displayName": [b"Ldap User"],
            "department": [b"Department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"111"],
        }
    ]

    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=ldap_users,
    )
    mocker.patch("invenio_app_ils.patrons.indexer.reindex_patrons")

    import_users()

    ldap_user = ldap_users[0]
    email = ldap_user_get(ldap_user, "mail").lower()
    user = User.query.filter(User.email == email).one()
    assert user

    assert UserProfile.query.filter(UserProfile.user_id == user.id).one()

    uid_number = ldap_user_get(ldap_user, "uidNumber")
    user_identity = UserIdentity.query.filter(
        UserIdentity.id == uid_number
    ).one()
    assert user_identity
    assert user_identity.method == OAUTH_REMOTE_APP_NAME
    assert RemoteAccount.query.filter(RemoteAccount.user_id == user.id).one()


def test_sync_users(app, db, testdata, mocker):
    """Test sync users with LDAP."""
    ldap_users = [
        {
            "displayName": [b"New user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"111"],
        },
        {
            "displayName": [b"A new name"],
            "department": [b"A new department"],
            "uidNumber": [b"222"],
            "mail": [b"ldap.user222@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"222"],
        },
        {
            "displayName": [b"Nothing changed"],
            "department": [b"Same department"],
            "uidNumber": [b"333"],
            "mail": [b"ldap.user333@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"333"],
        },
        {
            "displayName": [b"Name 1"],
            "department": [b"Department 1"],
            "uidNumber": [b"555"],
            "mail": [b"ldap.user555@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"555"],
        },
        {
            "displayName": [b"Name 2"],
            "department": [b"Department 2"],
            "uidNumber": [b"666"],
            "mail": [b"ldap.user555@cern.ch"],  # same email as 555
            "cernAccountType": [b"Primary"],
            "employeeID": [b"666"],
        },
        {
            "displayName": [b"Name"],
            "department": [b"Department"],
            "uidNumber": [b"777"],
            # missing email
            "cernAccountType": [b"Primary"],
            "employeeID": [b"777"],
        },
    ]

    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=ldap_users,
    )

    def _prepare():
        """Prepare data."""
        # Prepare users in DB. Use `LdapUserImporter` to make it easy
        # create old users
        WILL_BE_UPDATED = deepcopy(ldap_users[1])
        WILL_BE_UPDATED["displayName"] = [b"Previous name"]
        WILL_BE_UPDATED["department"] = [b"Old department"]
        LdapUserImporter().import_user(WILL_BE_UPDATED)

        WILL_NOT_CHANGE = deepcopy(ldap_users[2])
        LdapUserImporter().import_user(WILL_NOT_CHANGE)

        # create a user that does not exist anymore in LDAP, but will not
        # be deleted for safety
        COULD_BE_DELETED = {
            "displayName": [b"old user left CERN"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            "mail": [b"ldap.user444@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"444"],
        }
        LdapUserImporter().import_user(COULD_BE_DELETED)
        db.session.commit()
        reindex_patrons()

    _prepare()

    n_ldap, n_updated, n_added = update_users()

    current_search.flush_and_refresh(index="*")

    assert n_ldap == 6
    assert n_updated == 1
    assert n_added == 2

    invenio_users = User.query.all()
    assert len(invenio_users) == 6  # 5 from LDAP, 1 was already in test data

    patrons_search = PatronsSearch()

    def check_existence(expected_email, expected_name, expected_department):
        """Assert exist in DB and ES."""
        # check if saved in DB
        user = User.query.filter_by(email=expected_email).one()
        up = UserProfile.query.filter_by(user_id=user.id).one()
        assert up.full_name == expected_name
        ra = RemoteAccount.query.filter_by(user_id=user.id).one()
        assert ra.extra_data["department"] == expected_department

        # check if indexed correctly
        results = patrons_search.filter("term", id=user.id).execute()
        assert len(results.hits) == 1
        patron_hit = [r for r in results][0]
        assert patron_hit["email"] == expected_email
        assert patron_hit["department"] == expected_department

    check_existence("ldap.user111@cern.ch", "New user", "A department")
    check_existence("ldap.user222@cern.ch", "A new name", "A new department")
    check_existence(
        "ldap.user333@cern.ch", "Nothing changed", "Same department"
    )
    check_existence("ldap.user444@cern.ch", "old user left CERN", "Department")
    check_existence("ldap.user555@cern.ch", "Name 1", "Department 1")


def test_log_table(app):
    """Test that the log table works."""

    def find(log):
        return LdapSynchronizationLog.query.filter_by(id=log.id).one_or_none()

    # Basic insertion
    log = LdapSynchronizationLog.create_cli()
    found = find(log)
    assert found
    assert found.status == TaskStatus.RUNNING and found.agent == Agent.CLI
    found.query.delete()
    found = find(log)
    assert not found

    # Change state
    log = LdapSynchronizationLog.create_celery("1")
    found = find(log)
    assert found.status == TaskStatus.RUNNING and found.agent == Agent.CELERY
    assert found.task_id == "1"
    found.set_succeeded(5, 6, 7)
    found = find(log)
    assert found.status == TaskStatus.SUCCEEDED
    assert found.ldap_fetch_count == 5
    with pytest.raises(AssertionError):
        found.set_succeeded(1, 2, 3)
