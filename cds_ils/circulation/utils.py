# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Circulation configuration callbacks."""


def circulation_cds_extension_max_count(loan):
    """Return a default extensions max count."""
    unlimited = loan.get("extension_count", 0) + 1
    return unlimited
