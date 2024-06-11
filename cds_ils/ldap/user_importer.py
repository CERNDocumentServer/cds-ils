# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS invenio user importer API."""

from flask import current_app
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile

from cds_ils.config import OAUTH_REMOTE_APP_NAME


class LdapUserImporter:
    """Import ldap users to Invenio ILS records.

    Expected input format for ldap users:
        [
            {'givenName': [b'Joe'],
             'sn': [b'FOE'],
             'department': [b'IT/CDA'],
             'uidNumber': [b'100000'],
             'mail': [b'joe.foe@cern.ch'],
             'cernAccountType': [b'Primary'],
             'employeeID': [b'101010']
            },...
        ]
    """

    def __init__(self):
        """Constructor."""
        self.client_id = current_app.config["CERN_APP_OPENID_CREDENTIALS"][
            "consumer_key"
        ]

    def create_invenio_user(self, ldap_user):
        """Commit new user in db."""
        email = ldap_user["user_email"]
        user = User(email=email, active=True)
        db.session.add(user)
        db.session.commit()
        return user.id

    def create_invenio_user_identity(self, user_id, ldap_user):
        """Return new user identity entry."""
        uid_number = ldap_user["user_identity_id"]
        return UserIdentity(
            id=uid_number, method=OAUTH_REMOTE_APP_NAME, id_user=user_id
        )

    def create_invenio_user_profile(self, user_id, ldap_user):
        """Return new user profile."""
        display_name = "{0}, {1}".format(
            ldap_user["user_profile_last_name"], ldap_user["user_profile_first_name"]
        )
        return UserProfile(
            user_id=user_id,
            _displayname="id_{}".format(user_id),
            full_name=display_name,
        )

    def create_invenio_remote_account(self, user_id, ldap_user):
        """Return new user entry."""
        employee_id = ldap_user["remote_account_person_id"]
        department = ldap_user["remote_account_department"]
        mailbox = ldap_user["remote_account_mailbox"]
        return RemoteAccount.create(
            client_id=self.client_id,
            user_id=user_id,
            extra_data=dict(
                person_id=employee_id, department=department, mailbox=mailbox
            ),
        )

    def import_user(self, ldap_user):
        """Create Invenio users from LDAP export."""
        user_id = self.create_invenio_user(ldap_user)

        identity = self.create_invenio_user_identity(user_id, ldap_user)
        db.session.add(identity)

        profile = self.create_invenio_user_profile(user_id, ldap_user)
        db.session.add(profile)

        remote_account = self.create_invenio_remote_account(user_id, ldap_user)
        db.session.add(remote_account)

        return user_id
