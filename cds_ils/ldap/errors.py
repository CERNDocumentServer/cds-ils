# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS ldap exceptions."""
import sys


class InvalidLdapUser(Exception):
    """Invalid user exception."""

    def __init__(self, *args, log_func=None):
        """Constructor."""
        super().__init__(*args)
        print(args[0], file=sys.stderr)
        if log_func:
            log_func("ldap_user_has_no_email")
