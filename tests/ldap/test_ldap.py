# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Test LDAP functions."""

from copy import deepcopy
from unittest.mock import Mock

import pytest
from flask import current_app
from invenio_accounts.models import User
from invenio_app_ils.errors import AnonymizationActiveLoansError
from invenio_app_ils.patrons.search import PatronsSearch
from invenio_app_ils.proxies import current_app_ils
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_search import current_search
from invenio_userprofiles.models import UserProfile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from cds_ils.config import OAUTH_REMOTE_APP_NAME
from cds_ils.ldap.api import LdapUserImporter, delete_users, import_users, update_users
from cds_ils.ldap.models import Agent, LdapSynchronizationLog, TaskStatus
from cds_ils.ldap.tasks import synchronize_users_task
from cds_ils.ldap.utils import serialize_ldap_user


def test_import_users(app, db, testdata, mocker):
    """Test import of users from LDAP."""
    ldap_users = [
        {
            "givenName": [b"Ldap"],
            "sn": [b"User"],
            "department": [b"Department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"111"],
            "postOfficeBox": [b"M12345"],
        }
    ]

    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=ldap_users,
    )
    mocker.patch("invenio_app_ils.patrons.indexer.PatronIndexer.reindex_patrons")

    import_users()

    ldap_user_data = ldap_users[0]

    ldap_user = serialize_ldap_user(ldap_user_data)
    email = ldap_user["user_email"]
    user = User.query.filter(User.email == email).one()
    assert user

    assert UserProfile.query.filter(UserProfile.user_id == user.id).one()

    uid_number = ldap_user["user_identity_id"]
    user_identity = UserIdentity.query.filter(UserIdentity.id == uid_number).one()
    assert user_identity
    assert user_identity.method == OAUTH_REMOTE_APP_NAME
    assert RemoteAccount.query.filter(RemoteAccount.user_id == user.id).one()


def test_update_users(app, db, testdata, mocker):
    """Test update users with LDAP."""
    ldap_users = [
        {
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"A new"],
            "sn": [b"name"],
            "department": [b"A new department"],
            "uidNumber": [b"222"],
            "mail": [b"ldap.user222@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00222"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Nothing"],
            "sn": [b"changed"],
            "department": [b"Same department"],
            "uidNumber": [b"333"],
            "mail": [b"ldap.user333@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00333"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Name"],
            "sn": [b"1"],
            "department": [b"Department 1"],
            "uidNumber": [b"555"],
            "mail": [b"ldap.user555@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00555"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Name"],
            "sn": [b"2"],
            "department": [b"Department 2"],
            "uidNumber": [b"666"],
            "mail": [b"ldap.user555@cern.ch"],  # same email as 555
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00666"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Name"],
            "sn": [b"user"],
            "department": [b"Department"],
            "uidNumber": [b"777"],
            # missing email, should be skipped
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00777"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Name"],
            "sn": [b"user"],
            "department": [b"Department"],
            "uidNumber": [b"999"],
            # custom emails allowed
            "mail": [b"ldap.user999@test.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00999"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Nothing"],
            "sn": [b"changed"],
            "department": [b"Same department"],
            "uidNumber": [b"333"],
            # same email as 333, different employee ID, should be skipped
            "mail": [b"ldap.user333@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"9152364"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"Name"],
            "sn": [b"user"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            # empty email should be skipped
            "mail": [b""],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00444"],
            "postOfficeBox": [b"M12345"],
        },
    ]

    def _prepare():
        """Prepare data."""
        importer = LdapUserImporter()
        # Prepare users in DB. Use `LdapUserImporter` to make it easy
        # create old users
        WILL_BE_UPDATED = deepcopy(ldap_users[1])
        WILL_BE_UPDATED["displayName"] = [b"Previous name"]
        WILL_BE_UPDATED["department"] = [b"Old department"]
        ldap_user = serialize_ldap_user(WILL_BE_UPDATED)
        importer.import_user(ldap_user)

        WILL_NOT_CHANGE = deepcopy(ldap_users[2])
        ldap_user = serialize_ldap_user(WILL_NOT_CHANGE)
        importer.import_user(ldap_user)

        # create a user that does not exist anymore in LDAP, but will not
        # be deleted for safety
        COULD_BE_DELETED = {
            "givenName": [b"old user"],
            "sn": [b"left CERN"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            "mail": [b"ldap.user444@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00444"],
            "postOfficeBox": [b"M12345"],
        }
        ldap_user = serialize_ldap_user(COULD_BE_DELETED)
        importer.import_user(ldap_user)
        db.session.commit()
        current_app_ils.patron_indexer.reindex_patrons()

    def _prepare_duplicate():
        duplicated = {
            "givenName": [b"Name"],
            "sn": [b"2"],
            "department": [b"Department 2"],
            # same id as one of the previous, different emails
            # should be skipped
            "uidNumber": [b"555"],
            "mail": [b"other555@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00555"],
            "postOfficeBox": [b"M12345"],
        }
        importer = LdapUserImporter()
        ldap_user = serialize_ldap_user(duplicated)
        importer.import_user(ldap_user)
        db.session.commit()

    _prepare()

    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=ldap_users,
    )

    n_ldap, n_updated, n_added = update_users()

    current_search.flush_and_refresh(index="*")

    assert n_ldap == 9
    assert n_updated == 1  # 00222
    assert n_added == 3  # 00111, 00555, 00999

    invenio_users = User.query.all()
    # 2 are already in test data
    # 4 in the prepared data
    # 2 newly added from LDAP
    assert len(invenio_users) == 8

    patrons_search = PatronsSearch()

    def check_existence(
        expected_email,
        expected_name,
        expected_department,
        expected_person_id,
        expected_mailbox,
    ):
        """Assert exist in DB and ES."""
        # check if saved in DB
        user = User.query.filter_by(email=expected_email).one()
        up = UserProfile.query.filter_by(user_id=user.id).one()
        assert up.full_name == expected_name
        ra = RemoteAccount.query.filter_by(user_id=user.id).one()
        assert ra.extra_data["department"] == expected_department
        assert ra.extra_data["person_id"] == expected_person_id

        # check if indexed correctly
        results = patrons_search.filter("term", id=user.id).execute()
        assert len(results.hits) == 1
        patron_hit = [r for r in results][0]
        assert patron_hit["email"] == expected_email
        assert patron_hit["department"] == expected_department
        assert patron_hit["person_id"] == expected_person_id
        assert patron_hit["mailbox"] == expected_mailbox

    check_existence(
        "ldap.user111@cern.ch", "USER, New", "A department", "00111", "M12345"
    )
    check_existence(
        "ldap.user222@cern.ch",
        "NAME, A new",
        "A new department",
        "00222",
        "M12345",
    )
    check_existence(
        "ldap.user333@cern.ch",
        "CHANGED, Nothing",
        "Same department",
        "00333",
        "M12345",
    )
    check_existence(
        "ldap.user444@cern.ch",
        "LEFT CERN, old user",
        "Department",
        "00444",
        "M12345",
    )
    check_existence(
        "ldap.user555@cern.ch", "1, Name", "Department 1", "00555", "M12345"
    )

    # try ot import duplicated userUID
    with pytest.raises(IntegrityError):
        _prepare_duplicate()


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


def test_delete_user(app, db, testdata, mocker):
    """Test delete users when no longer in ldap."""

    ldap_users = [
        {
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"A new"],
            "sn": [b"name"],
            "department": [b"A new department"],
            "uidNumber": [b"222"],
            "mail": [b"ldap.user222@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00222"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"old user"],
            "sn": [b"left CERN"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            "mail": [b"ldap.user444@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00444"],
            "postOfficeBox": [b"M12345"],
        },
    ]

    new_ldap_response = [
        {
            "displayName": [b"New user"],
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        }
    ]

    def _prepare():
        """Prepare data."""
        importer = LdapUserImporter()
        # Prepare users in DB. Use `LdapUserImporter` to make it easy
        # create old users
        existing_user = deepcopy(ldap_users[0])
        ldap_user = serialize_ldap_user(existing_user)
        importer.import_user(ldap_user)

        user_to_delete1 = deepcopy(ldap_users[1])
        ldap_user = serialize_ldap_user(user_to_delete1)
        importer.import_user(ldap_user)

        user_to_delete2 = deepcopy(ldap_users[2])
        ldap_user = serialize_ldap_user(user_to_delete2)
        importer.import_user(ldap_user)

        db.session.commit()
        current_app_ils.patron_indexer.reindex_patrons()

    _prepare()
    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=new_ldap_response,
    )

    ldap_users_count, deleted_accounts = delete_users()

    assert ldap_users_count == 1
    # 2 from this test + 1 from testdata
    assert deleted_accounts == 3


def test_delete_user_with_counter(app, db, testdata, mocker):
    """Test delete users when no longer in ldap, after <n> checks."""

    ldap_users = [
        {
            "displayName": [b"New user"],
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"A new"],
            "sn": [b"name"],
            "department": [b"A new department"],
            "uidNumber": [b"222"],
            "mail": [b"ldap.user222@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00222"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"old user"],
            "sn": [b"left CERN"],
            "department": [b"Department"],
            "uidNumber": [b"444"],
            "mail": [b"ldap.user444@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00444"],
            "postOfficeBox": [b"M12345"],
        },
    ]

    new_ldap_response = [
        {
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        }
    ]

    def _prepare():
        """Prepare data."""
        importer = LdapUserImporter()
        # Prepare users in DB. Use `LdapUserImporter` to make it easy
        # create old users
        existing_user = deepcopy(ldap_users[0])
        ldap_user = serialize_ldap_user(existing_user)
        importer.import_user(ldap_user)

        user_to_delete1 = deepcopy(ldap_users[1])
        ldap_user = serialize_ldap_user(user_to_delete1)
        user_to_delete_id1 = importer.import_user(ldap_user)

        user_to_delete2 = deepcopy(ldap_users[2])
        ldap_user = serialize_ldap_user(user_to_delete2)
        user_to_delete_id2 = importer.import_user(ldap_user)

        db.session.commit()
        current_app_ils.patron_indexer.reindex_patrons()
        return user_to_delete_id1, user_to_delete_id2

    user_to_delete_id1, user_to_delete_id2 = _prepare()
    # mock LDAP response
    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=new_ldap_response,
    )

    ldap_users_count, deleted_accounts = delete_users(dry_run=False)

    assert ldap_users_count == 1
    assert deleted_accounts == 0

    ra1 = RemoteAccount.query.filter(RemoteAccount.user_id == user_to_delete_id1).one()
    ra2 = RemoteAccount.query.filter(RemoteAccount.user_id == user_to_delete_id2).one()

    assert ra1.extra_data["deletion_countdown"] == 1
    assert ra2.extra_data["deletion_countdown"] == 1

    # set to be deleted now
    config_checks_before_deletion = current_app.config["CDS_ILS_PATRON_DELETION_CHECKS"]

    # mark for total deletion
    ra2.extra_data["deletion_countdown"] = config_checks_before_deletion

    # unmark one entry
    fixed_ldap_response = [
        {
            "givenName": [b"New"],
            "sn": [b"user"],
            "department": [b"A department"],
            "uidNumber": [b"111"],
            "mail": [b"ldap.user111@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00111"],
            "postOfficeBox": [b"M12345"],
        },
        {
            "givenName": [b"A new"],
            "sn": [b"name"],
            "department": [b"A new department"],
            "uidNumber": [b"222"],
            "mail": [b"ldap.user222@cern.ch"],
            "cernAccountType": [b"Primary"],
            "employeeID": [b"00222"],
            "postOfficeBox": [b"M12345"],
        },
    ]

    mocker.patch(
        "cds_ils.ldap.api.LdapClient.get_primary_accounts",
        return_value=fixed_ldap_response,
    )

    ldap_users_count, deleted_accounts = delete_users(dry_run=False)

    assert ldap_users_count == 2
    # the users should be deleted (not the account from testdata
    # and not the unmarked)
    assert deleted_accounts == 1

    current_search.flush_and_refresh(index="*")

    ra1 = RemoteAccount.query.filter(RemoteAccount.user_id == user_to_delete_id1).one()

    # make sure first account was unmarked for deletion
    assert ra1.extra_data["deletion_countdown"] == 0

    # make sure account 2 was deleted
    with pytest.raises(NoResultFound):
        RemoteAccount.query.filter(RemoteAccount.user_id == user_to_delete_id2).one()


def test_send_email_on_error(app_with_notifs, mocker):
    """Test that an email is sent when an exception is raised."""
    mocker.patch(
        "cds_ils.ldap.api.get_ldap_users",
        side_effect=RuntimeError("exception triggered"),
    )

    with app_with_notifs.extensions["mail"].record_messages() as outbox:
        assert len(outbox) == 0
        synchronize_users_task()
        assert len(outbox) == 1
        email = outbox[0]
        assert email.recipients == [app_with_notifs.config["SUPPORT_EMAIL"]]

        def assert_contains(string):
            assert string in email.body
            assert string in email.html

        assert_contains("synchronize_users_task")
        assert_contains(RuntimeError.__name__)
        assert_contains("exception triggered")


def test_send_email_on_user_deletion_error(app_with_notifs, mocker):
    """Test that an email is sent when the user deletion failed."""
    # mock the users exit in LDAP

    def mock_get_patron(patron_id):
        from cds_ils.patrons.api import Patron

        class FakePatron(Patron):
            def __init__(self, id, revision_id=None):
                self.id = id
                self.revision_id = 1
                self.name = f"Patron{id}"
                self.email = f"patron{id}@cern.ch"

        return FakePatron(patron_id)

    mocker.patch("cds_ils.ldap.api.get_ldap_users", return_value=(2, {}, {}))
    mocker.patch(
        "invenio_app_ils.patrons.anonymization.current_app_ils.patron_cls.get_patron",
        mock_get_patron,
    )  # noqa
    mocker.patch(
        "invenio_app_ils.patrons.anonymization.current_app_ils.patron_indexer.delete"
    )  # noqa
    # mock RemoteAccounts
    mock1 = Mock()
    mock1.user_id = 1  # patron 1
    mock2 = Mock()
    mock2.user_id = 2  # patron 2
    mocker.patch("cds_ils.ldap.api.remap_invenio_users", return_value=[mock1, mock2])
    # mock that the any `InvenioUser` exist
    mocker.patch("cds_ils.ldap.api.InvenioUser")

    # mock anonymize, will raise because it has loans
    mocker.patch(
        "cds_ils.ldap.api.anonymize_patron_data",
        side_effect=AnonymizationActiveLoansError(
            "Cannot delete user {0}: found {1} active loans.".format(mock1.user_id, 4)
        ),
    )

    with app_with_notifs.extensions["mail"].record_messages() as outbox:
        assert len(outbox) == 0
        # delete without marking for deletion
        delete_users(dry_run=False, mark_for_deletion=False)
        assert len(outbox) == 1
        email = outbox[0]
        assert (
            email.recipients
            == app_with_notifs.config["ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS"]
        )

        def assert_contains(string):
            assert string in email.body
            assert string in email.html

        assert_contains("patron1@cern.ch")
        assert_contains("patron2@cern.ch")
