# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Test documents migration."""
from cds_ils.migrator.series import journal_marc21, serial_marc21
from cds_ils.migrator.xml_to_json_dump import CDSRecordDump
from tests.migrator.xml_imports.helpers import load_json


def test_migrate_record(datadir, base_app):
    """Test migrate date."""
    # [[ migrate the book ]]
    with base_app.app_context():
        data = load_json(datadir, "serial.json")
        dump = CDSRecordDump(data=data[0], dojson_model=serial_marc21)
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 213298
        assert res == {
            "_migration": {"record_type": "serial", "children": []},
            "mode_of_issuance": "SERIAL",
            "legacy_recid": 213298,
            "title": ["CERN Yellow Reports: Monographs"],
        }

        data = load_json(datadir, "serial2.json")
        dump = CDSRecordDump(data=data[0], dojson_model=serial_marc21)
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 436242
        assert res == {
            "_migration": {"record_type": "serial", "children": []},
            "mode_of_issuance": "SERIAL",
            "legacy_recid": 436242,
            "title": ["Traité de droit civil"],
        }
