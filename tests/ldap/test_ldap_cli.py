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
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile

from cds_ils.config import OAUTH_REMOTE_APP_NAME
from cds_ils.ldap.api import LdapUserImporter, _delete_invenio_user, \
    _update_invenio_user, import_ldap_users, ldap_user_get, sync_users
from cds_ils.ldap.models import Agent, LdapSynchronizationLog, TaskStatus


def test_send_email_delete_user_with_loans(app, patron1, testdata):
    """Test that email sent when the user is deleted with active loans."""
    with app.extensions["mail"].record_messages() as outbox:
        assert len(outbox) == 0
        _delete_invenio_user(patron1.id)
        assert len(outbox) == 1
        email = outbox[0]
        assert email.recipients == [
            app.config["MANAGEMENT_EMAIL"]
        ]

        def assert_contains(string):
            assert string in email.body
            assert string in email.html

        assert_contains("patron1@cern.ch")
        assert_contains("loanid-2")
        assert_contains("Prairie Fires: The American Dreams of Laura Ingalls"
                        " Wilder")


def test_update_user_from_ldap(app, db, patron1, testdata):
    """Test check for users update in sync command."""
    remote_account = RemoteAccount.query.join(User).one()
    ldap_user = {
        "displayName": [b"System User"],
        "department": [b"Another department"],
        "uidNumber": [b"1"],
        "mail": [b"system.user@cern.ch"],
        "cernAccountType": [b"Primary"],
        "employeeID": [b"1"],
    }
    _update_invenio_user(
        invenio_remote_account_id=remote_account.id, ldap_user=ldap_user
    )
    db.session.flush()

    remote_account = RemoteAccount.query.join(User).one()
    assert remote_account.extra_data["department"] == "Another department"


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

    import_ldap_users()

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
            "displayName": [b"Old user, but different department"],
            "department": [b"Changed department"],
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
        WILL_BE_UPDATED["department"] = [b"Old department"]
        LdapUserImporter().import_user(WILL_BE_UPDATED)

        WILL_NOT_CHANGE = deepcopy(ldap_users[2])
        LdapUserImporter().import_user(WILL_NOT_CHANGE)

        # create a user that does not exist anymore in LDAP
        WILL_BE_DELETED = {
            "displayName": [b"old user left CERN"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            "mail": [b"ldap.user444@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"444"],
        }
        LdapUserImporter().import_user(WILL_BE_DELETED)
        db.session.commit()

    _prepare()

    n_ldap, n_updated, n_deleted, n_added = sync_users()

    assert n_ldap == 3
    assert n_updated == 1
    assert n_deleted == 1
    assert n_added == 1

    invenio_users = User.query.all()
    assert len(invenio_users) == 4  # 3 from LDAP, 1 was already in test data

    user111 = User.query.filter_by(email="ldap.user111@cern.ch").one()
    ra = RemoteAccount.query.filter_by(user_id=user111.id).one()
    assert ra.extra_data["department"] == "A department"

    user222 = User.query.filter_by(email="ldap.user222@cern.ch").one()
    ra = RemoteAccount.query.filter_by(user_id=user222.id).one()
    assert ra.extra_data["department"] == "Changed department"

    user333 = User.query.filter_by(email="ldap.user333@cern.ch").one()
    ra = RemoteAccount.query.filter_by(user_id=user333.id).one()
    assert ra.extra_data["department"] == "Same department"

    assert User.query.filter_by(email="ldap.user444@cern.ch").count() == 0


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
    found.set_succeeded(5, 6, 7, 8)
    found = find(log)
    assert found.status == TaskStatus.SUCCEEDED
    assert found.ldap_fetch_count == 5
    with pytest.raises(AssertionError):
        found.set_succeeded(1, 2, 3, 4)
