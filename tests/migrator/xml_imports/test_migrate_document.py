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
        data = load_json(datadir, "book1.json")
        dump = CDSRecordDump(data=data[0])
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 262146
        assert res == {
            "agency_code": "SzGeCERN",
            "_created": "2001-03-19",
            "created_by": {"type": "user"},
            "number_of_pages": "465",
            "languages": ["ENG"],
            "title": "Gauge fields, knots and gravity",
            "legacy_recid": 262146,
            "provider_recid": "262146",
            "publication_year": "1994",
            "identifiers": [
                {"scheme": "ISBN", "value": "9789810217297"},
                {"scheme": "ISBN", "value": "9789810220341"},
                {"scheme": "ISBN", "value": "9810217293"},
                {"scheme": "ISBN", "value": "9810220340"},
            ],
            "authors": [
                {"full_name": "Baez, John C", "roles": ["AUTHOR"], "type": "PERSON"},
                {
                    "full_name": "Muniain, Javier P",
                    "roles": ["AUTHOR"],
                    "type": "PERSON",
                },
            ],
            "keywords": [
                {"source": "CERN", "value": "electromagnetism"},
                {"source": "CERN", "value": "gauge fields"},
                {"source": "CERN", "value": "general relativity"},
                {"source": "CERN", "value": "knot theory, applications"},
                {"source": "CERN", "value": "quantum gravity"},
            ],
            "internal_notes": [{"value": "newqudc"}],
            "document_type": "BOOK",
            "imprint": {
                "date": "1994-01-14",
                "publisher": "World Scientific",
                "place": "Singapore",
            },
            "tags": ["THESIS"],
            "_migration": {
                "has_related": False,
                "has_serial": False,
                "has_journal": False,
                "has_medium": False,
                "eitems_ebl": [],
                "eitems_safari": [],
                "eitems_external": [],
                "eitems_file_links": [],
                "eitems_has_ebl": False,
                "eitems_has_external": False,
                "eitems_has_files": False,
                "eitems_has_proxy": False,
                "eitems_has_safari": False,
                "eitems_open_access": False,
                "eitems_proxy": [],
                "item_medium": [],
                "is_multipart": False,
                "is_yellow_report": False,
                "journal_record_legacy_recids": [],
                "record_type": "document",
                "volumes": [],
                "serials": [],
                "tags": [],
                "related": [],
                "volumes_identifiers": [],
                "volumes_urls": [],
                "items": [],
                "conference_title": "",
                "eitems_internal_notes": "",
            },
        }
