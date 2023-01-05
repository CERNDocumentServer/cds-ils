# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Test documents migration."""
from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.migrator.series import journal_marc21
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump
from tests.migrator.xml_imports.helpers import load_json


def test_migrate_record(datadir, base_app):
    """Test migrate date."""
    # [[ migrate the book ]]
    with base_app.app_context():
        data = load_json(datadir, "journal.json")
        dump = CDSRecordDump(data=data[0], dojson_model=journal_marc21)
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 229384
        assert res == {
            "_created": "1992-01-21",
            "_migration": {
                "is_multipart": False,
                "has_related": True,
                "related": [
                    {
                        "related_recid": "229630",
                        "relation_type": "sequence",
                        "relation_description": None,
                        "sequence_order": "previous",
                    }
                ],
                "record_type": "journal",
                "volumes": [],
            },
            "mode_of_issuance": "SERIAL",
            "legacy_recid": 229384,
            "agency_code": "SzGeCERN",
            "alternative_titles": [
                {"type": "ABBREVIATION", "value": "Br. J. Appl. Phys."}
            ],
            "keywords": [
                {"value": "Institute of Physics", "source": "CERN"},
                {"value": "JPD", "source": "CERN"},
                {"value": "JPhysD", "source": "CERN"},
            ],
            "publisher": "IOP",
            "note": "Explanation of the series change: v 1 - 18 (1950-67); ser 2 v 1 - 2 (1968-69). Ser 2 subtitled: Journal of physics D",
            "internal_notes": [{"value": "Online archives purchased 2014"}],
            "access_urls": [
                {
                    "value": "http://iopscience.iop.org/0508-3443",
                    "description": "v 1 (1950) - v 18 (1967)",
                    "access_restriction": ["RESTRICTED_PERPETUAL_ACCESS_BACKFILES"],
                    "open_access": False,
                    "login_required": True,
                }
            ],
            "subjects": [{"value": "53", "scheme": "UDC"}],
            "title": "British journal of applied physics",
            "identifiers": [
                {"scheme": "ISSN", "value": "0508-3443", "material": "PRINT_VERSION"}
            ],
            "languages": ["ENG"],
            "series_type": "PERIODICAL",
            "physical_volumes": [
                {"description": "v 1 (1950) - v 18 (1967)", "location": "DE2"}
            ],
        }
