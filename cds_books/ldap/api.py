# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Books ldap API."""

import json
from datetime import datetime

import ldap
from flask import current_app
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile


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
        'mail',
        'displayName',
        'department',
        'cernAccountType',
        'employeeID',
        'uidNumber'
    ]

    def __init__(self, ldap_url):
        """Initialize ldap connection."""
        self.ldap = ldap.initialize(ldap_url)

    def get_primary_accounts(self):
        """Retrieve all primary accounts from ldap."""
        page_control = ldap.controls.SimplePagedResultsControl(
                            True, size=1000, cookie='')

        response = self.ldap.search_ext(
            'OU=Users,OU=Organic Units,DC=cern,DC=ch',
            ldap.SCOPE_ONELEVEL,
            '(&(cernAccountType=Primary))',
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[page_control]
        )

        result = []
        pages = 0
        while True:
            pages += 1
            rtype, rdata, rmsgid, serverctrls = self.ldap.result3(response)
            result.extend([x[1] for x in rdata])
            ldap_page_control = ldap.controls.SimplePagedResultsControl
            ldap_page_control_type = ldap_page_control.controlType
            controls = [control for control in serverctrls
                        if control.controlType == ldap_page_control_type]
            if not controls:
                print('The server ignores RFC 2696 control')
                break
            if not controls[0].cookie:
                break
            page_control.cookie = controls[0].cookie
            response = self.ldap.search_ext(
                'OU=Users,OU=Organic Units,DC=cern,DC=ch',
                ldap.SCOPE_ONELEVEL,
                '(&(cernAccountType=Primary))',
                self.LDAP_USER_RESP_FIELDS,
                serverctrls=[page_control]
            )
        return result

    def get_user_by_person_id(self, person_id):
        """Query ldap to retrieve user by person id."""
        self.ldap.search_ext(
            'OU=Users,OU=Organic Units,DC=cern,DC=ch',
            ldap.SCOPE_ONELEVEL,
            '(&(cernAccountType=Primary)(employeeID={}))'.format(person_id),
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[ldap.controls.SimplePagedResultsControl(
                True, size=7, cookie='')]
        )

        res = self.ldap.result()[1]

        return [x[1] for x in res]

    def get_user_by_mail(self, mail):
        """Query ldap to retrieve user by person id."""
        self.ldap.search_ext(
            'OU=Users,OU=Organic Units,DC=cern,DC=ch',
            ldap.SCOPE_ONELEVEL,
            '(&(cernAccountType=Primary)(mail={}))'.format(mail),
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[ldap.controls.SimplePagedResultsControl(
                True, size=7, cookie='')]
        )

        res = self.ldap.result()[1]

        return [x[1] for x in res]


class LdapUserImporter():
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
            'id': ldap_user['uidNumber'][0].decode("utf8"),
            'method': 'cern',
            'id_user': user_id,
        }

    def import_user(self, user):
        """Return new user entry."""
        return {
            'email': user['mail'][0].decode("utf8"),
            'active': True,
        }

    def import_remote_account(self, user_id, ldap_user):
        """Return new user entry."""
        return {
            'user_id': user_id,
            'extra_data': {
                'person_id': ldap_user['employeeID'][0].decode("utf8"),
                'department': ldap_user['department'][0].decode("utf8")
            }
        }

    def import_user_profile(self, user_id, ldap_user):
        """Return new user profile."""
        return {
            'user_id': user_id,
            '_displayname': 'id_' + str(user_id),
            'full_name': ldap_user['displayName'][0].decode("utf8"),
        }

    def import_users(self):
        """Return location and internal location records."""
        user_identities = []
        users_profiles = []
        remote_accounts = []

        def _commit_user(user_data):
            """Commit new user in db."""
            user = User(**self.import_user(user_data))
            db.session.add(user)
            db.session.commit()
            return user.id

        for ldap_user in self.ldap_users:
            user_id = _commit_user(ldap_user)

            identity = UserIdentity(
                **self.import_user_identity(user_id, ldap_user))
            db.session.add(identity)

            profile = UserProfile(
                **self.import_user_profile(user_id, ldap_user))
            db.session.add(profile)

            client_id = current_app.config.get(
                "CERN_APP_CREDENTIALS", {}).get("consumer_key") or "CLIENT_ID"
            remote_account = RemoteAccount(
                                client_id=client_id,
                                **self.import_remote_account(
                                    user_id, ldap_user))
            db.session.add(remote_account)

        db.session.commit()
