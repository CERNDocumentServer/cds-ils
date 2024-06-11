# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS ldap Client."""
import ldap
from flask import current_app


class LdapClient(object):
    """Ldap client class for user importation/synchronization.

    Response example:
        [
            {'givenName': [b'Joe'],
             'sn': [b'FOE'],
             'department': [b'IT/CDA'],
             'uidNumber': [b'100000'],
             'mail': [b'joe.foe@cern.ch'],
             'cernAccountType': [b'Primary'],
             'employeeID': [b'101010']
             'postOfficeBox': [b'JM12345']
            },...
        ]
    """

    LDAP_BASE = "OU=Users,OU=Organic Units,DC=cern,DC=ch"

    LDAP_CERN_PRIMARY_ACCOUNTS_FILTER = "(&(cernAccountType=Primary))"

    LDAP_USER_RESP_FIELDS = [
        "mail",
        "givenName",
        "sn",
        "department",
        "cernAccountType",
        "employeeID",
        "uidNumber",
        "postOfficeBox",
    ]

    def __init__(self, ldap_url=None):
        """Initialize ldap connection."""
        ldap_url = ldap_url or current_app.config["CDS_ILS_LDAP_URL"]
        self.ldap = ldap.initialize(ldap_url)

    def _search_paginated_primary_account(self, page_control):
        """Execute search to get primary accounts."""
        return self.ldap.search_ext(
            self.LDAP_BASE,
            ldap.SCOPE_ONELEVEL,
            self.LDAP_CERN_PRIMARY_ACCOUNTS_FILTER,
            self.LDAP_USER_RESP_FIELDS,
            serverctrls=[page_control],
        )

    def get_primary_accounts(self):
        """Retrieve all primary accounts from ldap."""
        page_control = ldap.controls.SimplePagedResultsControl(
            True, size=1000, cookie=""
        )

        result = []
        while True:
            response = self._search_paginated_primary_account(page_control)
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

        return result

    # Kept as example if needed to fetch a specific user by a field
    # def get_user_by_person_id(self, person_id):
    #     """Query ldap to retrieve user by person id."""
    #     self.ldap.search_ext(
    #         "OU=Users,OU=Organic Units,DC=cern,DC=ch",
    #         ldap.SCOPE_ONELEVEL,
    #         "(&(cernAccountType=Primary)(employeeID={}))".format(person_id),
    #         self.LDAP_USER_RESP_FIELDS,
    #         serverctrls=[
    #             ldap.controls.SimplePagedResultsControl(
    #                 True, size=7, cookie=""
    #             )
    #         ],
    #     )
    #
    #     res = self.ldap.result()[1]
    #
    #     return [x[1] for x in res]
