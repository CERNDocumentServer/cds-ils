# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Test documents migration."""

from cds_ils.migrator.xml_to_json_dump import CDSRecordDump
from tests.migrator.xml_imports.helpers import load_json


def test_migrate_record(datadir, base_app):
    """Test migrate date."""
    # [[ migrate the book ]]
    with base_app.app_context():
        data = load_json(datadir, "standard1.json")
        dump = CDSRecordDump(data=data[0])
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 1463268
        assert res == {
            "provider_recid": "1463268",
            "legacy_recid": 1463268,
            "agency_code": "SzGeCERN",
            "identifiers": [
                {"value": "ASTM-E467-08", "scheme": "STANDARD_NUMBER"},
                {"value": "ASTM-E-467-08", "scheme": "STANDARD_NUMBER"},
            ],
            "title": "Standard practice for verification of constant amplitude dynamic forces in an axial fatigue testing system",
            "publication_year": "2008",
            "imprint": {
                "date": "2008-01-01",
                "place": "West Conshohocken, PA",
                "publisher": "ASTM",
            },
            "document_type": "STANDARD",
            "number_of_pages": "11",
            "abstract": "1.1 This practice covers procedures for the dynamic verification of cyclic force amplitude control or measurement accuracy ....",
            "authors": [
                {
                    "full_name": "American Society for Testing and Materials. Philadelphia",
                    "type": "ORGANISATION",
                }
            ],
            "internal_notes": [
                {"value": "ASTM201207 - vol.03.01"},
                {"value": "BOTyhdiO1HVI.pdf"},
            ],
            "created_by": {"type": "user"},
            "_created": "2012-07-23",
            "languages": ["ENG"],
            "subjects": [{"value": "77.040.10", "scheme": "ICS"}],
            "_migration": {
                "record_type": "document",
                "volumes": [],
                "volumes_identifiers": [],
                "volumes_urls": [],
                "serials": [],
                "has_serial": False,
                "is_multipart": False,
                "is_yellow_report": False,
                "has_related": False,
                "has_journal": False,
                "tags": [],
                "journal_record_legacy_recids": [],
                "eitems_proxy": [],
                "eitems_has_proxy": False,
                "eitems_file_links": [
                    {
                        "url": {
                            "value": "http://cds.cern.ch/record/1463268/files/BOTyhdiO1HVI.pdf"
                        }
                    }
                ],
                "eitems_has_files": True,
                "eitems_external": [],
                "eitems_has_external": False,
                "eitems_ebl": [],
                "eitems_has_ebl": False,
                "eitems_safari": [],
                "eitems_has_safari": False,
                "eitems_open_access": False,
                "related": [],
                "items": [],
                "item_medium": [],
                "has_medium": False,
                "conference_title": "",
                "eitems_internal_notes": "",
            },
        }
