# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer module."""
CDS_ILS_IMPORTER_RECORD_TAG = "//*[local-name() = 'record']"

CDS_ILS_IMPORTER_PROVIDERS = {
    "cds": {
        "priority": 1,
        "agency_code": "SZeGeCERN",
    },
    "springer": {
        "priority": 2,
        "agency_code": "DE-He213",
    },
    "ebl": {"priority": 3, "agency_code": "MiAaPQ"},
    "safari": {"priority": 4, "agency_code": "CaSebORM"},
}
