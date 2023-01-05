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
        data = load_json(datadir, "multivolume.json")
        dump = CDSRecordDump(data=data[0], dojson_model=multipart_marc21)
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 104450
        assert res == {
            "_migration": {
                "record_type": "multipart",
                "volumes": [
                    {"title": "Early work (1905-1911)", "volume": "1"},
                    {"title": "Work on atomic physics (1912-1917)", "volume": "2"},
                    {
                        "title": "The correspondence principle (1918-1923)",
                        "volume": "3",
                    },
                    {"title": "The periodic system (1920-1923)", "volume": "4"},
                    {
                        "title": "The emergence of quantum mechanics (mainly 1924-1926)",
                        "volume": "5",
                    },
                    {
                        "title": "Foundations of quantum physics I (1926-1932)",
                        "volume": "6",
                    },
                    {
                        "title": "Foundations of quantum physics II (1933-1958)",
                        "volume": "7",
                    },
                    {
                        "title": "The penetration of charged particles through matter (1912-1954)",
                        "volume": "8",
                    },
                    {"title": "Nuclear physics (1929-1952)", "volume": "9"},
                    {
                        "title": "Complementarity beyond physics (1928-1962)",
                        "volume": "10",
                    },
                    {"title": "The political arena (1934-1961)", "volume": "11"},
                    {"title": "Popularization and people (1911-1962)", "volume": "12"},
                ],
                "volumes_identifiers": [
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "0444855012"}],
                        "physical_description": "print version",
                        "volume": "5",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "0444867120"}],
                        "physical_description": "print version",
                        "volume": "6",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "0444869298"}],
                        "physical_description": "print version",
                        "volume": "9",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "0444899723"}],
                        "physical_description": "print version",
                        "volume": "10",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "0720418003"}],
                        "physical_description": "print version",
                        "volume": "7",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080870991"}],
                        "physical_description": "electronic version",
                        "volume": "1",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871004"}],
                        "physical_description": "electronic version",
                        "volume": "2",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871011"}],
                        "physical_description": "electronic version",
                        "volume": "3",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871028"}],
                        "physical_description": "electronic version",
                        "volume": "4",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871035"}],
                        "physical_description": "electronic version",
                        "volume": "5",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871059"}],
                        "physical_description": "electronic version",
                        "volume": "7",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871066"}],
                        "physical_description": "electronic version",
                        "volume": "8",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780080871073"}],
                        "physical_description": "electronic version",
                        "volume": "9",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444513366"}],
                        "physical_description": "print version",
                        "volume": "11",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444529466"}],
                        "physical_description": "print version",
                        "volume": "12",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444865014"}],
                        "physical_description": "print version",
                        "volume": "5",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444867124"}],
                        "physical_description": "print version",
                        "volume": "6",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444869296"}],
                        "physical_description": "print version",
                        "volume": "9",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444870032"}],
                        "physical_description": "print version",
                        "volume": "8",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444898920"}],
                        "physical_description": "print version",
                        "volume": "7",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780444899729"}],
                        "physical_description": "print version",
                        "volume": "10",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780720418002"}],
                        "physical_description": "print version",
                        "volume": "7",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780720418019"}],
                        "physical_description": "print version",
                        "volume": "1",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780720418026"}],
                        "physical_description": "print version",
                        "volume": "2",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780720418033"}],
                        "physical_description": "print version",
                        "volume": "3",
                    },
                    {
                        "identifiers": [{"scheme": "ISBN", "value": "9780720418040"}],
                        "physical_description": "print version",
                        "volume": "4",
                    },
                ],
                "volumes_urls": [
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/4",
                                        "description": "ebook (v.4)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "4",
                    },
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/6",
                                        "description": "ebook (v.6)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "6",
                    },
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/7",
                                        "description": "ebook (v.7)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "7",
                    },
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/8",
                                        "description": "ebook (v.8)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "8",
                    },
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/9",
                                        "description": "ebook (v.9)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "9",
                    },
                    {
                        "_migration": {
                            "record_type": "document",
                            "eitems_proxy": [
                                {
                                    "url": {
                                        "value": "http://www.sciencedirect.com/science/bookseries/18760503/10",
                                        "description": "ebook (v.10)",
                                    },
                                    "open_access": False,
                                }
                            ],
                            "eitems_has_proxy": True,
                            "eitems_file_links": [],
                            "eitems_external": [],
                            "eitems_ebl": [],
                            "eitems_safari": [],
                        },
                        "volume": "10",
                    },
                ],
                "serials": [],
                "has_serial": False,
                "is_multipart": True,
                "is_yellow_report": False,
                "has_related": False,
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
                "eitems_internal_notes": "ELS201605",
                "related": [],
                "items": [
                    {"barcode": "72-2408-2", "volume": "1"},
                    {"barcode": "B00014307", "volume": "10"},
                    {"barcode": "CM-B00059276", "volume": "11"},
                    {"barcode": "CM-B00059277", "volume": "12"},
                    {"barcode": "82-0165-9", "volume": "2"},
                    {"barcode": "76-0846-6", "volume": "3"},
                    {"barcode": "77-0542-9", "volume": "4"},
                    {"barcode": "85-0045-6", "volume": "5"},
                    {"barcode": "85-0828-5", "volume": "6"},
                    {"barcode": "B00002600", "volume": "7"},
                    {"barcode": "B00009616", "volume": "7"},
                    {"barcode": "88-0037-7", "volume": "8"},
                    {"barcode": "86-0361-5", "volume": "9"},
                ],
                "item_medium": [],
                "has_medium": False,
                "conference_title": "",
                "multivolume_record": True,
            },
            "mode_of_issuance": "MULTIPART_MONOGRAPH",
            "provider_recid": "104450",
            "legacy_recid": 104450,
            "agency_code": "SzGeCERN",
            "languages": ["ENG"],
            "subjects": [
                {"value": "53(08)", "scheme": "UDC"},
                {"value": "53", "scheme": "UDC"},
                {"value": "92", "scheme": "UDC"},
                {"value": "539.17.014", "scheme": "UDC"},
                {"value": "539.171.01", "scheme": "UDC"},
                {"value": "537.534.75", "scheme": "UDC"},
                {"value": "539.186.2", "scheme": "UDC"},
            ],
            "authors": [
                {
                    "full_name": "Bohr, Niels Henrik David",
                    "roles": ["AUTHOR"],
                    "type": "PERSON",
                },
                {"full_name": "Nielsen, J Rud", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Hoyer, Ulrich", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Rosenfeld, Léon", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Ruedinger, Erik", "roles": ["EDITOR"], "type": "PERSON"},
                {
                    "full_name": "Stolzenburg, Klaus",
                    "roles": ["EDITOR"],
                    "type": "PERSON",
                },
                {"full_name": "Kalckar, Jørgen", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Thorsen, Jens", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Aaserud, Finn", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Favrhold, David", "roles": ["EDITOR"], "type": "PERSON"},
            ],
            "alternative_titles": [{"type": "SUBTITLE", "value": "collected works"}],
            "title": "Niels Bohr",
            "publication_year": "1976 - 2006",
            "imprint": {
                "date": "1976-01-01 - 2006-01-01 ",
                "place": "Amsterdam",
                "publisher": "North-Holland",
            },
            "number_of_volumes": "12",
            "internal_notes": [{"value": "EBLlink deleted"}],
            "source": "ELS",
            "_created": "1985-01-07",
            "keywords": [{"value": "correspondence", "source": "CERN"}],
            "document_type": "BOOK",
            "created_by": {"type": "batchuploader"},
        }
