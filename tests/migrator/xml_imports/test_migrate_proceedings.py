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
        data = load_json(datadir, "proceedings1.json")
        dump = CDSRecordDump(data=data[0])
        dump.prepare_revisions()
        res = dump.revisions[-1][1]
        assert res["legacy_recid"] == 2213126
        assert res == {
            "provider_recid": "2213126",
            "legacy_recid": 2213126,
            "agency_code": "SzGeCERN",
            "created_by": {"type": "batchuploader"},
            "_created": "2017-05-01",
            "publication_year": "2016",
            "languages": ["ENG"],
            "volume": "(v.1)",
            "source": "SPR",
            "authors": [
                {"full_name": "Qian, Tao", "roles": ["EDITOR"], "type": "PERSON"},
                {"full_name": "Rodino, Luigi", "roles": ["EDITOR"], "type": "PERSON"},
            ],
            "document_type": "PROCEEDINGS",
            "identifiers": [
                {
                    "value": "9783319419435",
                    "scheme": "ISBN",
                    "material": "PRINT_VERSION",
                },
                {
                    "value": "10.1007/978-3-319-41945-9",
                    "material": "DIGITAL",
                    "scheme": "DOI",
                },
                {
                    "value": "10.1007/978-3-319-48812-7",
                    "material": "DIGITAL",
                    "scheme": "DOI",
                },
            ],
            "subjects": [
                {"value": "QA370-380", "scheme": "LOC"},
                {"value": "515.353", "scheme": "DEWEY"},
            ],
            "conference_info": [
                {
                    "title": "10th International ISAAC Congress",
                    "place": "Macau, China",
                    "dates": "2015-08-03 - 2015-08-08",
                    "identifiers": [{"scheme": "CERN", "value": "macau20150803"}],
                    "series": "10",
                    "country": "CHN",
                    "acronym": "ISAAC 2015",
                }
            ],
            "imprint": {"date": "2016-01-01", "place": "Cham", "publisher": "Springer"},
            "internal_notes": [{"value": "Mathematics and statistics"}],
            "table_of_content": [
                "Leon Cohen: A review of Brownian motion based solely on the Langevin equation with white noise",
                "Darren Crowdy: Geometry-fitted Fourier-Mellin transform pairs",
                "Alan McIntosh , Sylvie Monniaux: First order approach to L^p estimates for the Stokes operator on Lipschitz domains",
                "Zhong-Can Ou-Yang, Zhan-Chun Tu: The study of complex shapes of fluid membranes, the Helfrich functional and new applications",
                "Maximilian Reich, Winfried Sickel: Multiplication and composition in weighted modulation spaces",
                "Saburou Saitoh: A reproducing kernel theory with some general applications",
                "Vladimir Temlyakov: Sparse approximation by greedy algorithms",
                "Dan-Virgil Voiculescu: The bi-free extension of free probability",
                "Ya-Guang Wang: Stability of the Prandtl boundary layers",
                "Elias Wegert: Visual exploration of complex functions",
                "Karen Yagdjian: Integral transform approach to time-dependent partial differential equations.",
            ],
            "abstract": "This book collects lectures given by the plenary speakers at the 10th International ISAAC Congress, held in Macau, China in 2015. The contributions, authored by eminent specialists, present some of the most exciting recent developments in mathematical analysis, probability theory, and related applications. Topics include: partial differential equations in mathematical physics, Fourier analysis, probability and Brownian motion, numerical analysis, and reproducing kernels. The volume also presents a lecture on the visual exploration of complex functions using the domain coloring technique. Thanks to the accessible style used, readers only need a basic command of calculus.",
            "_migration": {
                "record_type": "document",
                "volumes": [],
                "volumes_identifiers": [],
                "volumes_urls": [],
                "serials": [
                    {
                        "title": "Springer proceedings in mathematics & statistics",
                        "volume": "177",
                        "issn": "2194-1009",
                    }
                ],
                "has_serial": True,
                "is_multipart": False,
                "is_yellow_report": False,
                "has_related": False,
                "has_journal": False,
                "tags": [],
                "journal_record_legacy_recids": [],
                "eitems_external": [
                    {
                        "url": {
                            "description": "e-proceedings (v.1)",
                            "value": "http://dx.doi.org/10.1007/978-3-319-41945-9",
                        },
                        "open_access": False,
                    },
                    {
                        "url": {
                            "description": "e-proceedings (v.2)",
                            "value": "http://dx.doi.org/10.1007/978-3-319-48812-7",
                        },
                        "open_access": False,
                    },
                ],
                "eitems_has_proxy": False,
                "eitems_file_links": [],
                "eitems_has_files": False,
                "eitems_proxy": [],
                "eitems_has_external": True,
                "eitems_ebl": [],
                "eitems_has_ebl": False,
                "eitems_safari": [],
                "eitems_has_safari": False,
                "eitems_open_access": False,
                "related": [],
                "items": [],
                "item_medium": [],
                "has_medium": False,
                "conference_title": "10th International ISAAC Congress",
                "eitems_internal_notes": "SPR201609; SPR201705",
            },
        }
