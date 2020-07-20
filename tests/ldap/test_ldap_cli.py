# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, print_function

from invenio_accounts.models import User
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile

from cds_books.ldap.cli import check_user_for_update, import_ldap_users


def test_check_users_for_update(app, system_user):
    """Test check for users update in sync command."""
    with app.app_context():
        user = RemoteAccount.query.join(User).one()
        ldap_user = {
            'displayName': [b'System User'],
            'department': [b'Another department'],
            'uidNumber': [b'1'],
            'mail': [b'system.user@cern.ch'],
            'cernAccountType': [b'Primary'],
            'employeeID': [b'1']
        }
        check_user_for_update(user, ldap_user)
        assert user.extra_data["department"] == "Another department"


def test_import_ldap_users(app):
    """Test that ldap user is created."""
    ldap_users = [{
        'displayName': [b'Ldap User'],
        'department': [b'Department'],
        'uidNumber': [b'1'],
        'mail': [b'ldap.user@cern.ch'],
        'cernAccountType': [b'Primary'],
        'employeeID': [b'1']
    }]

    import_ldap_users(ldap_users)

    user = User.query.filter(
        User.email == ldap_users[0]["mail"][0].decode("utf8")).one()
    assert user

    assert UserProfile.query.filter(UserProfile.user_id == user.id).one()
    assert UserIdentity.query.filter(
        UserIdentity.id == ldap_users[0]["uidNumber"][0].decode("utf8")).one()
    assert RemoteAccount.query.filter(RemoteAccount.user_id == user.id).one()
