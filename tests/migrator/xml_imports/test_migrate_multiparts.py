# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Test documents migration."""
from cds_ils.migrator.series import multipart_marc21
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump
from tests.migrator.xml_imports.helpers import load_json


def test_migrate_record(datadir, base_app):
    """Test migrate date."""
    # [[ migrate the book ]]
    with base_app.app_context():
        data = load_json(datadir, "multiparts.json")
        dump = CDSRecordDump(data=data[0], dojson_model=multipart_marc21)
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 2758857
        assert res == {
            "_migration": {
                "record_type": "multipart",
                "volumes": [{"title": "Optics", "volume": "1"}],
                "volumes_identifiers": [],
                "volumes_urls": [],
                "serials": [],
                "has_serial": False,
                "is_multipart": True,
                "is_yellow_report": False,
                "has_related": True,
                "has_journal": False,
                "tags": [],
                "journal_record_legacy_recids": [],
                "eitems_proxy": [],
                "eitems_has_proxy": False,
                "eitems_file_links": [],
                "eitems_has_files": False,
                "eitems_external": [],
                "eitems_has_external": False,
                "eitems_ebl": [],
                "eitems_safari": [],
                "eitems_has_ebl": False,
                "eitems_has_safari": False,
                "eitems_open_access": False,
                "eitems_internal_notes": "",
                "related": [
                    {
                        "related_recid": "244535",
                        "relation_type": "edition",
                        "relation_description": "1st ed.",
                    },
                    {
                        "related_recid": "1084451",
                        "relation_type": "edition",
                        "relation_description": "2nd ed.",
                    },
                ],
                "items": [],
                "item_medium": [],
                "has_medium": False,
                "conference_title": "",
                "multipart_id": "VOL10048",
                "multivolume_record": False,
            },
            "mode_of_issuance": "MULTIPART_MONOGRAPH",
            "provider_recid": "2758857",
            "legacy_recid": 2758857,
            "agency_code": "SzGeCERN",
            "document_type": "BOOK",
            "authors": [
                {
                    "full_name": "Teich, Malvin Carl",
                    "roles": ["AUTHOR"],
                    "type": "PERSON",
                },
                {
                    "full_name": "Saleh, Bahaa E A",
                    "roles": ["AUTHOR"],
                    "type": "PERSON",
                },
            ],
            "edition": "3rd",
            "created_by": {"type": "user"},
            "_created": "2021-03-29",
            "title": "Fundamentals of photonics",
            "publication_year": "2019",
            "imprint": {
                "date": "2019-01-01",
                "place": "Hoboken, NJ",
                "publisher": "Wiley",
            },
            "identifiers": [
                {"scheme": "ISBN", "value": "9781119506874", "material": "HARDBACK"}
            ],
            "languages": ["ENG"],
        }
