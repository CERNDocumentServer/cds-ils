# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.
"""Book fields tests."""

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from cds_dojson.marc21.utils import create_record
from dojson.errors import MissingRule

from cds_ils.importer.errors import ManualImportRequired, \
    MissingRequiredField, UnexpectedValue
from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.models.book import model
from cds_ils.importer.providers.cds.rules.values_mapping import MATERIALS, \
    mapping

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    model._default_fields = {"_migration": {**get_helper_dict()}}

    record = model.do(blob, ignore_missing=False)

    expected = {
        "_migration": {**get_helper_dict()},
    }

    expected.update(**json_body)
    assert record == expected


def test_mapping():
    """Test mapping."""
    with pytest.raises(UnexpectedValue):
        assert mapping(MATERIALS, "softwa", raise_exception=True) == "software"


def test_subject_classification(app):
    """Test subject classification."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="082" ind1="0" ind2="4">
                <subfield code="a">515.353</subfield>
                <subfield code="2">23</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "515.353", "scheme": "Dewey"}]},
        )
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA76.642</subfield>
                <subfield code="b">XXXX</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "QA76.642", "scheme": "LoC"}]},
        )
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2=" ">
                <subfield code="a">QA76.642</subfield>
                <subfield code="b">XXXX</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "QA76.642", "scheme": "LoC"}]},
        )
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA76.642</subfield>
            </datafield>
            <datafield tag="082" ind1=" " ind2=" ">
                <subfield code="a">005.275</subfield>
            </datafield>
            """,
            {
                "subjects": [
                    {"value": "QA76.642", "scheme": "LoC"},
                    {"value": "005.275", "scheme": "Dewey"},
                ]
            },
        )
        check_transformation(
            """
            <datafield tag="080" ind1=" " ind2=" ">
                <subfield code="a">528</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "528", "scheme": "UDC"}]},
        )
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="a">25040.40</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "25040.40", "scheme": "ICS"}]},
        )
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">13.75.Jz</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">13.60.Rj</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">14.20.Jn</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">25.80.Nv</subfield>
            </datafield>
            """,
            {},
        )
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">CERN Yellow Report</subfield>
                <subfield code="a">CERN-2018-003-CP</subfield>
            </datafield>
            """,
            {},
        )


def test_created_by_email(app):
    """Test acquisition email."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "_email": "karolina.przerwa@cern.ch",
                    "type": "user",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
            </datafield>
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "type": "user",
                    "_email": "karolina.przerwa@cern.ch",
                },
                "_created": "2018-07-16",
            },
        )


def test_created(app):
    """Test created dates."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR201701</subfield>
            </datafield>
            """,
            {"source": "SPR", "_created": "2017-01-01"},
        )
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">random text</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">random text</subfield>
            </datafield>
            """,
            {
                "internal_notes": [
                    {"value": "random text"},
                ]
            },
        )
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR201701</subfield>
            </datafield>
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "type": "user",
                    "_email": "karolina.przerwa@cern.ch",
                },
                "source": "SPR",
                "_created": "2017-01-01",
            },
        )


def test_collections(app):
    """Test collections."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIB"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIB"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIB"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBINTLAW</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIBINTLAW"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["BOOKSHOP"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["BOOKSHOP"],
                    "has_tags": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBLEGRES</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIBLEGRES"],
                    "has_tags": True,
                },
            },
        )


def test_document_type(app):
    """Test document type."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """,
            {
                "document_type": "BOOK",
            },
        )
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">21</subfield>
            </datafield>
            """,
            {
                "document_type": "BOOK",
            },
        )
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">42</subfield>
            </datafield>
            """,
            {
                "document_type": "PROCEEDINGS",
            },
        )
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">43</subfield>
            </datafield>
            """,
            {
                "document_type": "PROCEEDINGS",
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="b">REPORT</subfield>
            </datafield>
            """,
            {"document_type": "BOOK"},
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="697" ind1="C" ind2=" ">
                    <subfield code="a">virTScvyb</subfield>
                </datafield>
                """,
                {"document_type": "BOOK"},
            )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="697" ind1="C" ind2=" ">
                    <subfield code="b">ENGLISH BOOK CLUB</subfield>
                </datafield>
                <datafield tag="960" ind1=" " ind2=" ">
                    <subfield code="a">21</subfield>
                </datafield>
                """,
                {"document_type": "BOOK"},
            )


def test_document_type_collection(app):
    """Test document type collection."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIB"],
                    "has_tags": True,
                },
                "document_type": "BOOK",
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">BOOK</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "tags": ["LEGSERLIB"],
                    "has_tags": True,
                },
                "document_type": "BOOK",
            },
        )


def test_urls(app):
    """Test urls."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="8">1336159</subfield>
                <subfield code="s">726479</subfield>
                <subfield code="u">
                    http://cds.cern.ch/record/1393420/files/NF-EN-13480-2-AC6.pdf
                </subfield>
                <subfield code="y">
                Description
                </subfield>
            </datafield>
        """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_files": True,
                    "eitems_file_links": [
                        {
                            "description": "Description",
                            "value": "http://cds.cern.ch/record/1393420/files/NF-EN-13480-2-AC6.pdf",
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="8564" ind1=" " ind2=" ">
                <subfield code="u">https://cds.cern.ch/record/12345/files/abc.pdf</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_files": True,
                    "eitems_file_links": [
                        {
                            "value": "https://cds.cern.ch/record/12345/files/abc.pdf"
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="8">1336158</subfield>
                <subfield code="s">2445021</subfield>
                <subfield code="u">http://awesome.domain/with/a/path</subfield>
            </datafield>
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="8">1336157</subfield>
                <subfield code="s">2412918</subfield>
                <subfield code="u">http://another.domain/with/a/path</subfield>
                <subfield code="x">pdfa</subfield>
            </datafield>
            """,
            {
                "urls": [
                    {"value": "http://awesome.domain/with/a/path"},
                    {"value": "http://another.domain/with/a/path"},
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">
                https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560
                </subfield>
                <subfield code="y">ebook</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_ebl": True,
                    "eitems_ebl": [
                        {
                            "value": "https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560"
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">https://learning.oreilly.com/library/view/-/9781118491300/?ar</subfield>
                <subfield code="y">ebook</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_external": True,
                    "eitems_external": [
                        {
                            "value": "https://learning.oreilly.com/library/view/-/9781118491300/?ar"
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">
                https://ezproxy.cern.ch/login?url=https://www.worldscientific.com/toc/rast/10
                </subfield>
                <subfield code="y">ebook</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_proxy": True,
                    "eitems_proxy": [
                        {
                            "value": "https://www.worldscientific.com/toc/rast/10"
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">
                https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560
                </subfield>
                <subfield code="y">ebook</subfield>
            </datafield>
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">
                https://learning.oreilly.com/library/view/-/9781118491300/?ar
                </subfield>
                <subfield code="y">ebook</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_has_ebl": True,
                    "eitems_ebl": [
                        {
                            "value": "https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560"
                        },
                    ],
                    "eitems_external": [
                        {
                            "value": "https://learning.oreilly.com/library/view/-/9781118491300/?ar"
                        },
                    ],
                    "eitems_has_external": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="8564" ind1=" " ind2=" ">
                <subfield code="u">google.com</subfield>
                <subfield code="y">description</subfield>
            </datafield>
            """,
            {
                "urls": [
                    {"value": "google.com", "description": "description"}
                ],
            },
        )


def test_authors(app):
    """Test authors."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Frampton, Paul H</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Glashow, Sheldon Lee</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Van Dam, Hendrik</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">Seyfert, Paul</subfield>
                <subfield code="0">AUTHOR|(INSPIRE)INSPIRE-00341737</subfield>
                <subfield code="0">AUTHOR|(SzGeCERN)692828</subfield>
                <subfield code="0">AUTHOR|(CDS)2079441</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="m">paul.seyfert@cern.ch</subfield>
                <subfield code="9">#BEARD#</subfield>
            </datafield>
            <datafield tag="720" ind1=" " ind2=" ">
                <subfield code="a">Neubert, Matthias</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">John Doe</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="u">Univ. Gent</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">Jane Doe</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="u">Univ. Gent</subfield>
            </datafield>
            """,
            {
                "authors": [
                    {
                        "full_name": "Frampton, Paul H",
                        "roles": ["EDITOR"],
                        "alternative_names": "Neubert, Matthias",
                    },
                    {"full_name": "Glashow, Sheldon Lee", "roles": ["EDITOR"]},
                    {"full_name": "Van Dam, Hendrik", "roles": ["EDITOR"]},
                    {
                        "full_name": "Seyfert, Paul",
                        "roles": ["AUTHOR"],
                        "affiliations": [{"name": "CERN"}],
                        "identifiers": [
                            {
                                "scheme": "INSPIRE ID",
                                "value": "INSPIRE-00341737",
                            },
                            {"scheme": "CERN", "value": "692828"},
                            {"scheme": "CDS", "value": "2079441"},
                        ],
                    },
                    {
                        "full_name": "John Doe",
                        "roles": ["AUTHOR"],
                        "affiliations": [
                            {"name": "CERN"},
                            {"name": "Univ. Gent"},
                        ],
                    },
                    {
                        "full_name": "Jane Doe",
                        "roles": ["AUTHOR"],
                        "affiliations": [
                            {"name": "CERN"},
                            {"name": "Univ. Gent"},
                        ],
                    },
                ],
            },
        )

        check_transformation(
            """
             <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Frampton, Paul H</subfield>
                <subfield code="e">ed.</subfield>
                <subfield code="u">et al.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Glashow, Sheldon Lee</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            """,
            {
                "authors": [
                    {
                        "full_name": "Frampton, Paul H",
                        "roles": ["EDITOR"],
                    },
                    {"full_name": "Glashow, Sheldon Lee", "roles": ["EDITOR"]},
                ],
                "other_authors": True,
            },
        )

        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="700" ind1=" " ind2=" ">
                    <subfield code="a">Langrognat, B</subfield>
                </datafield>
                <datafield tag="700" ind1=" " ind2=" ">
                    <subfield code="a">Sauniere, J</subfield>
                    <subfield code="e">et al.</subfield>
                </datafield>
                """,
                {},
            )


# better example to be provided
def test_corporate_author(app):
    """Test corporate author."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="a"> Springer</subfield>
            </datafield>
            """,
            {
                "authors": [{"full_name": "Springer", "type": "ORGANISATION"}],
            },
        )
        check_transformation(
            """
            <datafield tag="110" ind1=" " ind2=" ">
                <subfield code="a">Marston, R M</subfield>
            </datafield>
            """,
            {
                "authors": [
                    {"full_name": "Marston, R M", "type": "ORGANISATION"},
                ],
            },
        )


def test_collaborations(app):
    """Test_collaborations."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="5">PH-EP</subfield>
            </datafield>
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="g">ATLAS Collaboration</subfield>
            </datafield>
            """,
            {
                "authors": [
                    {"full_name": "PH-EP", "type": "ORGANISATION"},
                    {"full_name": "ATLAS", "type": "ORGANISATION"},
                ]
            },
        )


def test_publication_info(app):
    """Test publication info."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="v">42</subfield>
                <subfield code="w">C19-01-08.1</subfield>
            </datafield>
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="n">BOOK</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "page_start": 1692,
                        "page_end": 1695,
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "journal_volume": "42",
                        "material": "BOOK",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="v">42</subfield>
            </datafield>
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="n">fsihfifri</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "page_start": 1692,
                        "page_end": 1695,
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "journal_volume": "42",
                    }
                ],
                "conference_info": {
                    "identifiers": [
                        {"scheme": "CERN_CODE", "value": "fsihfifri"}
                    ]
                },
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="773" ind1=" " ind2=" ">
                    <subfield code="c">10-95-5</subfield>
                    <subfield code="n">10</subfield>
                    <subfield code="y">2007</subfield>
                    <subfield code="p">Radiat. Meas.</subfield>
                    <subfield code="v">42</subfield>
                </datafield>
                """,
                {
                    "publication_info": [
                        {
                            "page_start": 1692,
                            "page_end": 1695,
                            "year": 2007,
                            "journal_title": "Radiat. Meas.",
                            "journal_issue": "10",
                            "journal_volume": "42",
                        }
                    ]
                },
            )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {"note": "1692 numebrs text etc Random text"}
                ]
            },
        )
        check_transformation(
            """
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="b">2155631</subfield>
                <subfield code="n">genoa20160330</subfield>
                <subfield code="k">1</subfield>
            </datafield>
            """,
            {
                "document_type": "PERIODICAL_ISSUE",
                "_migration": {
                    **get_helper_dict(),
                    "journal_record_legacy_recid": "2155631",
                    "has_journal": True,
                },
                "conference_info": {
                    "identifiers": [
                        {"scheme": "CERN_CODE", "value": "genoa20160330"}
                    ]
                },
                "publication_info": [
                    {
                        "page_start": 1,
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "page_start": 1692,
                        "page_end": 1695,
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "note": "1692 numebrs text etc Random text",
                    }
                ]
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="773" ind1=" " ind2=" ">
                    <subfield code="c">1692-1695-2000</subfield>
                    <subfield code="n">10</subfield>
                    <subfield code="y">2007</subfield>
                    <subfield code="p">Radiat. Meas.</subfield>
                    <subfield code="o">1692 numebrs text etc</subfield>
                    <subfield code="x">Random text</subfield>
                </datafield>
                """,
                {
                    "publication_info": [
                        {
                            "page_start": 1692,
                            "page_end": 1695,
                            "year": 2007,
                            "journal_title": "Radiat. Meas.",
                            "journal_issue": "10",
                            "pubinfo_freetext": "1692 numebrs "
                            "text etc Random text",
                        }
                    ]
                },
            )


def test_extensions(app):
    """Test extensions"""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="925" ind1=" " ind2=" ">
                <subfield code="i">applicable at CERN</subfield>
                <subfield code="p">Expert ICS-25.160</subfield>
                <subfield code="z">Reviewed in December 2019</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "standard_review:applicability": "applicable at CERN",
                    "standard_review:checkdate": "Reviewed in December 2019",
                    "standard_review:expert": "Expert ICS-25.160",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="925" ind1=" " ind2=" ">
                <subfield code="i">no longer applicable</subfield>
                <subfield code="p">Expert ICS-25.160</subfield>
                <subfield code="v">withdrawn</subfield>
                <subfield code="z">Reviewed in December 2019</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "standard_review:applicability": "no longer applicable",
                    "standard_review:validity": "withdrawn",
                    "standard_review:checkdate": "Reviewed in December 2019",
                    "standard_review:expert": "Expert ICS-25.160",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            <datafield tag="925" ind1=" " ind2=" ">
                <subfield code="i">no longer applicable</subfield>
                <subfield code="p">Expert ICS-25.160</subfield>
                <subfield code="v">withdrawn</subfield>
                <subfield code="z">Reviewed in December 2019</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "unit:accelerator": ["CERN LHC"],
                    "unit:experiment": ["ATLAS", "CMS"],
                    "unit:project": ["FCC"],
                    "standard_review:applicability": "no longer applicable",
                    "standard_review:validity": "withdrawn",
                    "standard_review:checkdate": "Reviewed in December 2019",
                    "standard_review:expert": "Expert ICS-25.160",
                }
            },
        )


def test_related_record(app):
    """Test related record."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="775" ind1=" " ind2=" ">
                <subfield code="b">Test text</subfield>
                <subfield code="c">Random text</subfield>
                <subfield code="w">748392</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "748392",
                            "relation_type": "Test text",
                        }
                    ],
                },
            },
        )
        with pytest.raises(ManualImportRequired):
            check_transformation(
                """
                <datafield tag="787" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="w">7483924</subfield>
                </datafield>
                """,
                {
                    "_migration": {
                        **get_helper_dict(),
                        "has_related": True,
                        "related": [
                            {
                                "related_recid": "7483924",
                                "relation_type": "other",
                            }
                        ],
                    },
                },
            )
        check_transformation(
            """
            <datafield tag="775" ind1=" " ind2=" ">
                <subfield code="w">7483924</subfield>
            </datafield>
            <datafield tag="787" ind1=" " ind2=" ">
                <subfield code="w">748</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "has_related": True,
                    "related": [
                        {"related_recid": "7483924", "relation_type": "other"},
                        {"related_recid": "748", "relation_type": "other"},
                    ],
                },
            },
        )


def test_accelerator_experiments(app):
    """Test accelerator experiments."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "unit:accelerator": ["CERN LHC"],
                    "unit:experiment": ["ATLAS", "CMS"],
                    "unit:project": ["FCC"],
                }
            },
        )


def test_isbns(app):
    """Test isbns."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "value": "9781630814434",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0691090858</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780691090856</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781400889167</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="u">electronic version</subfield>
                <subfield code="z">9780691090849</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="u">electronic version</subfield>
                <subfield code="z">9780691090849</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"value": "0691090858", "scheme": "ISBN"},
                    {"value": "9780691090856", "scheme": "ISBN"},
                    {
                        "value": "9781400889167",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9780691090849",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                ],
            },
        )
        with pytest.raises(ManualImportRequired):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="q">(electronic bk.)</subfield>
                    <subfield code="u">electronic version</subfield>
                    <subfield code="b">electronic version</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="u">electronic version</subfield>
                </datafield>
                """,
                {
                    "identifiers": [
                        {
                            "medium": "electronic version",
                            "scheme": "ISBN",
                        },
                        {
                            "medium": "electronic version",
                            "scheme": "ISBN",
                        },
                    ],
                },
            )
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "value": "9781630814434",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                ],
                "volume": "(v.1)",
            },
        )

        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">description</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "value": "9781630814434",
                        "description": "description",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "medium": "electronic version",
                        "scheme": "ISBN",
                    },
                ],
                "volume": "(v.1)",
            },
        )

        with pytest.raises(ManualImportRequired):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="a">9781630814434</subfield>
                    <subfield code="q">(electronic bk.)</subfield>
                    <subfield code="u">electronic version (v.2)</subfield>
                    <subfield code="b">electronic version</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="a">9781630811051</subfield>
                    <subfield code="u">electronic version (v.1)</subfield>
                </datafield>
                """,
                {
                    "identifiers": [
                        {
                            "value": "9781630814434",
                            "medium": "electronic version",
                            "scheme": "ISBN",
                        },
                        {
                            "value": "9781630811051",
                            "medium": "electronic version",
                            "scheme": "ISBN",
                        },
                    ],
                    "volume": "(v.1)",
                },
            )


def test_report_numbers(app):
    """Test report numbers."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1808.02335</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {"value": "arXiv:1808.02335", "scheme": "arXiv"}
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="a">hep-th/9509119</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"value": "hep-th/9509119", "scheme": "REPORT_NUMBER"}
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1808.02335</subfield>
                <subfield code="c">hep-ex</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "value": "arXiv:1808.02335",
                        "scheme": "arXiv",
                    }
                ],
                "subjects": [
                    {
                        "scheme": "arXiv",
                        "value": "hep-ex",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1808.02335</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "value": "arXiv:1808.02335",
                        "scheme": "arXiv",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="z">CERN-THESIS-2018-004</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "value": "CERN-THESIS-2018-004",
                        "hidden": True,
                        "scheme": "REPORT_NUMBER",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">CERN-ISOLDE-2018-001</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "value": "CERN-ISOLDE-2018-001",
                        "hidden": True,
                        "scheme": "REPORT_NUMBER",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="a">NAPAC-2016-MOPOB23</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="9">ATL-COM-PHYS-2018-980</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="z">ATL-COM-PHYS-2017</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"value": "NAPAC-2016-MOPOB23", "scheme": "REPORT_NUMBER"},
                    {
                        "value": "ATL-COM-PHYS-2018-980",
                        "hidden": True,
                        "scheme": "REPORT_NUMBER",
                    },
                    {
                        "value": "ATL-COM-PHYS-2017",
                        "hidden": True,
                        "scheme": "REPORT_NUMBER",
                    },
                ],
            },
        )
        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="037" ind1=" " ind2=" ">
                    <subfield code="x">hep-th/9509119</subfield>
                </datafield>
                """,
                {
                    "identifiers": [
                        {"value": "hep-th/9509119", "scheme": "REPORT_NUMBER"}
                    ],
                },
            )
        with pytest.raises(MissingRule):
            check_transformation(
                """
                <datafield tag="695" ind1=" " ind2=" ">
                    <subfield code="9">LANL EDS</subfield>
                    <subfield code="a">math-ph</subfield>
                </datafield>
                """,
                {},
            )


def test_dois(app):
    """Test dois."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1007/978-1-4613-0247-6</subfield>
                <subfield code="q">data</subfield>
                <subfield code="9">source</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "source": "source",
                        "material": "data",
                        "value": "10.1007/978-1-4613-0247-6",
                        "scheme": "DOI",
                    }
                ],
            },
        )


def test_alternative_identifiers(app):
    """Test external system identifiers."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">EBL</subfield>
                <subfield code="a">5231528</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "scheme": "EBL",
                        "value": "5231528",
                    }
                ],
            },
        )

        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">inspire-cnum</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">Inspire</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """,
            {
                "conference_info": {
                    "identifiers": [
                        {"scheme": "INSPIRE_CNUM", "value": "2365039"}
                    ],
                },
                "alternative_identifiers": [
                    {
                        "scheme": "Inspire",
                        "value": "2365039",
                    }
                ],
            },
        )

        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="035" ind1=" " ind2=" ">
                    <subfield code="9">Random</subfield>
                    <subfield code="a">2365039</subfield>
                </datafield>
                """,
                {},
            )

        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">CERCER</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """,
            {},
        )

        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">SLAC</subfield>
                <subfield code="a">5231528</subfield>
            </datafield>
            """,
            {},
        )

        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">ASIN</subfield>
                <subfield code="a">9402409580</subfield>
                <subfield code="9">DLC</subfield>
            </datafield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">EBL</subfield>
                <subfield code="a">5231528</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "value": "5231528",
                        "scheme": "EBL",
                    }
                ]
            },
        )

        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1007/s00269-016-0862-1</subfield>
            </datafield>
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1103/PhysRevLett.121.052004</subfield>
            </datafield>
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="9">arXiv</subfield>
                <subfield code="a">10.1103/PhysRevLett.121.052004</subfield>
                <subfield code="q">publication</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"value": "10.1007/s00269-016-0862-1", "scheme": "DOI"},
                    {
                        "value": "10.1103/PhysRevLett.121.052004",
                        "scheme": "DOI",
                    },
                    {
                        "value": "10.1103/PhysRevLett.121.052004",
                        "scheme": "DOI",
                        "material": "publication",
                        "source": "arXiv",
                    },
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="036" ind1=" " ind2=" ">
                <subfield code="9">DLC</subfield>
                <subfield code="a">92074207</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "scheme": "DLC",
                        "value": "92074207",
                    }
                ],
            },
        )
        # ignore 035__9 == arXiv
        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">5231528</subfield>
            </datafield>
            """,
            {
                # "alternative_identifiers": [
                #     {"scheme": "arXiv", "value": "5231528"}
                # ]
            },
        )


def test_arxiv_eprints(app):
    """Test arxiv eprints."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math-ph</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "scheme": "arXiv",
                        "value": "arXiv:1209.5665",
                    }
                ],
                "subjects": [{"scheme": "arXiv", "value": "math-ph"}],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math-ph</subfield>
            </datafield>
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math.GT</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {"value": "arXiv:1209.5665", "scheme": "arXiv"}
                ],
                "subjects": [
                    {"scheme": "arXiv", "value": "math-ph"},
                    {"scheme": "arXiv", "value": "math.GT"},
                ],
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="037" ind1=" " ind2=" ">
                    <subfield code="9">arXiv</subfield>
                    <subfield code="a">arXiv:1209.5665</subfield>
                    <subfield code="c">math-phss</subfield>
                </datafield>
                """,
                {
                    "arxiv_eprints": [
                        {
                            "categories": ["math-ph"],
                            "value": "arXiv:1209.5665",
                        }
                    ],
                },
            )


def test_languages(app):
    """Test languages."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">eng</subfield>
            </datafield>
            """,
            {
                "languages": ["EN"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">english</subfield>
            </datafield>
            """,
            {
                "languages": ["EN"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">fre</subfield>
            </datafield>
            """,
            {
                "languages": ["FR"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">pl</subfield>
            </datafield>
            """,
            {
                "languages": ["PL"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">ger</subfield>
            </datafield>
            """,
            {
                "languages": ["DE"],
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="041" ind1=" " ind2=" ">
                    <subfield code="a">xxxxxxxx</subfield>
                </datafield>
                """,
                {
                    "languages": ["DE"],
                },
            )


def test_editions(app):
    """Test editions."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="250" ind1=" " ind2=" ">
                <subfield code="a">3rd ed.</subfield>
            </datafield>
            """,
            {"edition": "3rd"},
        )


def test_imprint(app):
    """Test imprints."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="260" ind1=" " ind2=" ">
                <subfield code="a">Sydney</subfield>
                <subfield code="b">Allen &amp; Unwin</subfield>
                <subfield code="c">2013</subfield>
                <subfield code="g">2015</subfield>
            </datafield>
            """,
            {
                "publication_year": "2013",
                "imprint": {
                    "place": "Sydney",
                    "publisher": "Allen & Unwin",
                    "date": "2013",
                    "reprint_date": "2015",
                },
            },
        )


@pytest.mark.skip
def test_preprint_date(app):
    """Test preprint date."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="269" ind1=" " ind2=" ">
                <subfield code="a">Geneva</subfield>
                <subfield code="b">CERN</subfield>
                <subfield code="c">19 Jan 2016</subfield>
            </datafield>
            """,
            {
                "preprint_date": "2016-01-19",
            },
        )
        check_transformation(
            """
            <datafield tag="269" ind1=" " ind2=" ">
                <subfield code="a">Geneva</subfield>
                <subfield code="b">CERN</subfield>
            </datafield>
            """,
            {},
        )
        with pytest.raises(ManualImportRequired):
            check_transformation(
                """
                <datafield tag="269" ind1=" " ind2=" ">
                    <subfield code="a">Geneva</subfield>
                    <subfield code="b">CERN</subfield>
                    <subfield code="c">33 Jan 2016</subfield>
                </datafield>
                """,
                {
                    "preprint_date": "2016-01-19",
                },
            )


def test_number_of_pages(app):
    """Test number of pages."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">373 p</subfield>
            </datafield>
            """,
            {
                "number_of_pages": "373",
            },
        )
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">480 p. ; 1 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                "number_of_pages": "480",
                "physical_copy_description": "1 CD-ROM",
            },
        )
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">42 p. ; 2 CD-ROM ; 1 DVD, 1 vhs</subfield>
            </datafield>
            """,
            {
                "number_of_pages": "42",
                "physical_copy_description": "2 CD-ROM, 1 DVD, 1 VHS",
            },
        )
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a"></subfield>
            </datafield>
            """,
            {},
        )
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">mult. p</subfield>
            </datafield>
            """,
            {},
        )

        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">2 v</subfield>
                </datafield>
                """,
                {},
            )
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">42 p. + 17 p</subfield>
                </datafield>
                """,
                {},
            )
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">
                        amendment A1 (18 p) + amendment A2 (18 p)
                    </subfield>
                </datafield>
                """,
                {},
            )
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">
                        amendment A1 (18 p) + amendment A2 (18 p)
                    </subfield>
                </datafield>
                """,
                {},
            )
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">42 p. ; E22</subfield>
                </datafield>
                """,
                {},
            )


def test_abstracts(app):
    """Test abstracts."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">The publication...</subfield>
            </datafield>
            """,
            {
                "abstract": "The publication...",
            },
        )
        check_transformation(
            """
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">The publication...</subfield>
                <subfield code="9">arXiv</subfield>
            </datafield>
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">Does application...</subfield>
            </datafield>
            """,
            {
                "abstract": "The publication...",
                "alternative_abstracts": ["Does application..."],
            },
        )
    with pytest.raises(MissingRequiredField):
        check_transformation(
            """
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
            </datafield>
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">Does application...</subfield>
            </datafield>
            """,
            {"abstract": "Does application..."},
        )


@pytest.mark.skip
def test_funding_info(app):
    """Test funding info."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="a">CERN Technical Student Program</subfield>
            </datafield>
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="a">FP7</subfield>
                <subfield code="c">654168</subfield>
                <subfield code="f">AIDA-2020</subfield>
                <subfield code="r">openAccess</subfield>
            </datafield>
            """,
            {
                "funding_info": [
                    {
                        "agency": "CERN Technical Student Program",
                    },
                    {
                        "agency": "FP7",
                        "grant_number": "654168",
                        "project_number": "AIDA-2020",
                        "openaccess": True,
                    },
                ]
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="536" ind1=" " ind2=" ">
                    <subfield code="a">
                        CERN Technical Student Program
                    </subfield>
                </datafield>
                <datafield tag="536" ind1=" " ind2=" ">
                    <subfield code="a">FP7</subfield>
                    <subfield code="c">654168</subfield>
                    <subfield code="f">AIDA-2020</subfield>
                    <subfield code="r">openAccedafss</subfield>
                </datafield>
                """,
                {
                    "funding_info": [
                        {
                            "agency": "CERN Technical Student Program",
                        },
                        {
                            "agency": "FP7",
                            "grant_number": "654168",
                            "project_number": "AIDA-2020",
                            "openaccess": True,
                        },
                    ]
                },
            )


def test_license(app):
    """Test license."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="b">arXiv</subfield>
                <subfield code="u">
                    http://arxiv.org/licenses/nonexclusive-distrib/1.0/
                </subfield>
            </datafield>
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">Preprint</subfield>
                <subfield code="a">CC-BY-4.0</subfield>
            </datafield>
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">Publication</subfield>
                <subfield code="a">CC-BY-4.0</subfield>
                <subfield code="f">SCOAP3</subfield>
                <subfield code="g">DAI/7161287</subfield>
            </datafield>
            """,
            {
                "licenses": [
                    {
                        "license": {
                            "url": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
                            "name": None,
                        }
                    },
                    {
                        "license": {
                            "name": "CC-BY-4.0",
                            "url": None,
                        },
                        "material": "preprint",
                    },
                    {
                        "license": {
                            "name": "CC-BY-4.0",
                            "url": None,
                        },
                        "material": "publication",
                        "internal_note": "DAI/7161287",
                    },
                ]
            },
        )


def test_copyright(app):
    """Test copyright."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="d">d</subfield>
                <subfield code="f">f</subfield>
                <subfield code="g">2013</subfield>
                <subfield code="u">u</subfield>
            </datafield>
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="3">Preprint</subfield>
                <subfield code="d">CERN</subfield>
                <subfield code="g">2018</subfield>
            </datafield>
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="f">This work is licensed.</subfield>
                <subfield code="u">
                    http://creativecommons.org/licenses/by/4.0
                </subfield>
            </datafield>
            """,
            {
                "copyrights": [
                    {
                        "holder": "d",
                        "statement": "f",
                        "year": 2013,
                        "url": "u",
                    },
                    {"material": "preprint", "holder": "CERN", "year": 2018},
                    {
                        "statement": "This work is licensed.",
                        "url": "http://creativecommons.org/licenses/by/4.0",
                    },
                ]
            },
        )


def test_conference_info(app):
    """Test conference info."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">INSPIRE-CNUM</subfield>
                <subfield code="a">1234</subfield>
            </datafield>
            <datafield tag="111" ind1=" " ind2=" ">
                <subfield code="9">20040621</subfield>
                <subfield code="a">2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics
                </subfield>
                <subfield code="c">Bari, Italy</subfield>
                <subfield code="d">21 Jun 2004</subfield>
                <subfield code="f">2004</subfield>
                <subfield code="g">bari20040621</subfield>
                <subfield code="n">2</subfield>
                <subfield code="w">IT</subfield>
                <subfield code="z">20040621</subfield>
            </datafield>
            <datafield tag="711" ind1=" " ind2=" ">
                <subfield code="a">SNGHEGE2004</subfield>
            </datafield>
            """,
            {
                "conference_info": {
                    "identifiers": [
                        {"scheme": "INSPIRE_CNUM", "value": "1234"},
                        {"scheme": "CERN_CODE", "value": "bari20040621"},
                    ],
                    "title": """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                    "place": "Bari, Italy",
                    "dates": "2004-06-21 - 2004-06-21",
                    "series": {"number": 2},
                    "country": "IT",
                    "acronym": "SNGHEGE2004",
                }
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="111" ind1=" " ind2=" ">
                    <subfield code="9">20040621</subfield>
                    <subfield code="a">2nd Workshop on Science with
                     the New Generation of High Energy Gamma-ray Experiments:
                     between Astrophysics and Astroparticle Physics
                    </subfield>
                    <subfield code="c">Bari, Italy</subfield>
                    <subfield code="d">21 Jun 2004</subfield>
                    <subfield code="f">2004</subfield>
                    <subfield code="g">bari20040621</subfield>
                    <subfield code="n">2</subfield>
                    <subfield code="w">ITALIA</subfield>
                    <subfield code="z">20040621</subfield>
                </datafield>

                """,
                {
                    "conference_info": {
                        "title": """2nd Workshop on Science with the New
                             Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                        "place": "Bari, Italy",
                        "identifiers": [
                            {"scheme": "CERN_CODE", "value": "bari20040621"},
                        ],
                        "dates": "2004-06-21 - 2004-06-21",
                        "series": {"number": 2},
                        "country_code": "IT",
                        "contact": "arantza.de.oyanguren.campos@cern.ch",
                    }
                },
            )
            with pytest.raises(UnexpectedValue):
                check_transformation(
                    """
                    <datafield tag="111" ind1=" " ind2=" ">
                        <subfield code="9">2gtrw</subfield>
                        <subfield code="a">2nd Workshop on Science with
                         the New Generation of High Energy Gamma-ray Experiments:
                         between Astrophysics and Astroparticle Physics
                        </subfield>
                        <subfield code="c">Bari, Italy</subfield>
                        <subfield code="d">gbrekgk</subfield>
                        <subfield code="f">2004</subfield>
                        <subfield code="g">bari20040621</subfield>
                        <subfield code="n">2</subfield>
                        <subfield code="w">IT</subfield>
                        <subfield code="z">2treht</subfield>
                    </datafield>
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                        </subfield>
                    </datafield>
                    <datafield tag="711" ind1=" " ind2=" ">
                        <subfield code="a">SNGHEGE2004</subfield>
                    </datafield>
                    """,
                    {
                        "conference_info": {
                            "title": """2nd Workshop on Science with the New
                             Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                            "place": "Bari, Italy",
                            "cern_conference_code": "bari20040621",
                            "opening_date": "2004-06-21",
                            "series_number": 2,
                            "country_code": "IT",
                            "closing_date": "2004-06-21",
                            "contact": "arantza.de.oyanguren.campos@cern.ch",
                            "acronym": "SNGHEGE2004",
                        }
                    },
                )
            with pytest.raises(MissingRequiredField):
                check_transformation(
                    """
                    <datafield tag="270" ind1=" " ind2=" ">
                        <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                        </subfield>
                    </datafield>
                    """,
                    {
                        "conference_info": {
                            "contact": "arantza.de.oyanguren.campos@cern.ch"
                        }
                    },
                )


def test_alternative_titles_a(app):
    """Test title translations."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="242" ind1=" " ind2=" ">
                <subfield code="9">submitter</subfield>
                <subfield code="a">Study of the impact of stacking on simple
                      hard diffraction events in CMS/LHC</subfield>
                <subfield code="b">Subtitle/LHC</subfield>
            </datafield>
            """,
            {
                "alternative_titles": [
                    {
                        "value": """Study of the impact of stacking on simple
                      hard diffraction events in CMS/LHC""",
                        "language": "EN",
                        "type": "TRANSLATED_TITLE",
                    },
                    {
                        "value": "Subtitle/LHC",
                        "language": "EN",
                        "type": "TRANSLATED_SUBTITLE",
                    },
                ]
            },
        )


def test_title(app):
    """Test title."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Incoterms 2010</subfield>
                <subfield code="b">les règles de l'ICC</subfield>
            </datafield>
            """,
            {
                "title": "Incoterms 2010",
                "alternative_titles": [
                    {"value": "les règles de l'ICC", "type": "SUBTITLE"}
                ],
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="245" ind1=" " ind2=" ">
                    <subfield code="a">Incoterms 2010</subfield>
                    <subfield code="b">les règles de l'ICC</subfield>
                </datafield>
                <datafield tag="245" ind1=" " ind2=" ">
                    <subfield code="a">With duplicate title</subfield>
                </datafield>
                """,
                {},
            )


def test_alternative_titles(app):
    """Test alternative titles."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Air quality — sampling</subfield>
                <subfield code="b">
                    part 4: guidance on the metrics
                </subfield>
                <subfield code="i">CERN</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                    part 15: guidance on preservation
                </subfield>
            </datafield>
            """,
            {
                "alternative_titles": [
                    {
                        "value": "Air quality — sampling",
                        "type": "ALTERNATIVE_TITLE",
                    },
                    {
                        "value": """part 4: guidance on the metrics""",
                        "type": "SUBTITLE",
                    },
                    {
                        "value": "Water quality — sampling",
                        "type": "ALTERNATIVE_TITLE",
                    },
                    {
                        "value": """part 15: guidance on preservation""",
                        "type": "SUBTITLE",
                    },
                ]
            },
        )
    with app.app_context():
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                    part 15: guidance on the preservation
                </subfield>
            </datafield>
            """,
            {
                "document_type": "BOOK",
                "alternative_titles": [
                    {
                        "value": "Water quality — sampling",
                        "type": "ALTERNATIVE_TITLE",
                    },
                    {
                        "value": """part 15: guidance on the preservation""",
                        "type": "SUBTITLE",
                    },
                ],
            },
        )


def test_note(app):
    """Test public notes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">
            Translated from ...
            </subfield>
            </datafield>
            <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">No CD-ROM</subfield>
            </datafield>
            """,
            {"note": """Translated from ... / No CD-ROM"""},
        )
        check_transformation(
            """
            <datafield tag="500" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">
                    Comments: Book, 380 p.,
                </subfield>
            </datafield>
            """,
            {"note": """Comments: Book, 380 p.,"""},
        )


def test_table_of_contents(app):
    """Test table of contents."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="505" ind1="0" ind2=" ">
                <subfield code="a">
                2nd Advanced School on Exoplanetary Science: Astrophysics of Exoplanetary Atmospheres -- Chapter 1: Modeling Exoplanetary Atmospheres, by Jonathan J. Fortney -- Chapter 2: Observational Techniques, by David Sing -- Chapter 3: Molecular spectroscopy for Exoplanets by Jonathan Tennyson -- Chapter 4: Solar system atmospheres by Davide Grassi.
                </subfield>
            </datafield>
            """,
            {
                "table_of_content": [
                    "2nd Advanced School on Exoplanetary Science: Astrophysics of Exoplanetary Atmospheres",
                    "Chapter 1: Modeling Exoplanetary Atmospheres, by Jonathan J. Fortney",
                    "Chapter 2: Observational Techniques, by David Sing",
                    "Chapter 3: Molecular spectroscopy for Exoplanets by Jonathan Tennyson",
                    "Chapter 4: Solar system atmospheres by Davide Grassi.",
                ]
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="505" ind1="0" ind2=" ">
                    <subfield code="a">
                    </subfield>
                </datafield>
                """,
                {"table_of_content": []},
            )


def test_standard_numbers(app):
    """Tests standard number field translation."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="a">FD-X-60-000</subfield>
            </datafield>
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="a">NF-EN-13306</subfield>
            </datafield>
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="b">BS-EN-ISO-6507-2</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"value": "FD-X-60-000", "scheme": "STANDARD_NUMBER"},
                    {"value": "NF-EN-13306", "scheme": "STANDARD_NUMBER"},
                    {
                        "value": "BS-EN-ISO-6507-2",
                        "hidden": True,
                        "scheme": "STANDARD_NUMBER",
                    },
                ]
            },
        )
        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="021" ind1=" " ind2=" ">
                    <subfield code="c">FD-X-60-000</subfield>
                </datafield>
                """,
                {
                    "identifiers": [
                        {"value": "FD-X-60-000", "scheme": "STANDARD_NUMBER"},
                        {"value": "NF-EN-13306", "scheme": "STANDARD_NUMBER"},
                        {
                            "value": "BS-EN-ISO-6507-2",
                            "hidden": True,
                            "scheme": "STANDARD_NUMBER",
                        },
                    ]
                },
            )


def test_book_series(app):
    """Tests book series field translation."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Minutes</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "serials": [
                        {"title": "Minutes", "issn": None, "volume": None}
                    ],
                    "has_serial": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">
                    De Gruyter studies in mathematical physics
                </subfield>
                <subfield code="v">16</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "serials": [
                        {
                            "title": "De Gruyter studies in mathematical physics",
                            "issn": None,
                            "volume": "16",
                        }
                    ],
                    "has_serial": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Springer tracts in modern physics</subfield>
                <subfield code="v">267</subfield>
                <subfield code="x">0081-3869</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "serials": [
                        {
                            "title": "Springer tracts in modern physics",
                            "issn": "0081-3869",
                            "volume": "267",
                        }
                    ],
                    "has_serial": True,
                }
            },
        )


def test_541(app):
    """Test 541."""
    with app.app_context():
        with pytest.raises(MissingRule):
            check_transformation(
                """
                <record>
                    <controlfield tag="001">2654497</controlfield>
                    <controlfield tag="003">SzGeCERN</controlfield>
                    <datafield tag="980" ind1=" " ind2=" ">
                        <subfield code="a">BOOK</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Cai, Baoping</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Liu, Yonghong</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Hu, Jinqiu</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Liu, Zengkai</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Wu, Shengnan</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="700" ind1=" " ind2=" ">
                        <subfield code="a">Ji, Renjie</subfield>
                        <subfield code="e">ed.</subfield>
                    </datafield>
                    <datafield tag="035" ind1=" " ind2=" ">
                        <subfield code="9">SCEM</subfield>
                        <subfield code="a">90.20.00.192.6</subfield>
                    </datafield>
                    <datafield tag="690" ind1="C" ind2=" ">
                        <subfield code="a">BOOK</subfield>
                    </datafield>
                    <datafield tag="697" ind1="C" ind2=" ">
                        <subfield code="a">BOOKSHOP</subfield>
                    </datafield>
                    <datafield tag="541" ind1=" " ind2=" ">
                        <subfield code="9">85.00</subfield>
                    </datafield>
                    <datafield tag="916" ind1=" " ind2=" ">
                        <subfield code="d">201901</subfield>
                        <subfield code="s">h</subfield>
                        <subfield code="w">201904</subfield>
                    </datafield>
                    <datafield tag="300" ind1=" " ind2=" ">
                        <subfield code="a">401 p</subfield>
                    </datafield>
                    <datafield tag="080" ind1=" " ind2=" ">
                        <subfield code="a">519.226</subfield>
                    </datafield>
                    <datafield tag="245" ind1=" " ind2=" ">
                        <subfield code="a">
                            Bayesian networks in fault diagnosis
                        </subfield>
                        <subfield code="b">practice and application</subfield>
                    </datafield>
                    <datafield tag="260" ind1=" " ind2=" ">
                        <subfield code="a">Singapore</subfield>
                        <subfield code="b">World Scientific</subfield>
                        <subfield code="c">2019</subfield>
                    </datafield>
                    <datafield tag="020" ind1=" " ind2=" ">
                        <subfield code="a">9789813271487</subfield>
                        <subfield code="u">print version, hardback</subfield>
                    </datafield>
                    <datafield tag="041" ind1=" " ind2=" ">
                        <subfield code="a">eng</subfield>
                    </datafield>
                    <datafield tag="960" ind1=" " ind2=" ">
                        <subfield code="a">21</subfield>
                    </datafield>
                </record>
                """,
                {
                    "agency_code": "SzGeCERN",
                    # 'acquisition_source': {
                    #     'datetime': "2019-01-21"
                    # },
                    "creation_date": "2019-01-21",
                    "_collections": ["BOOKSHOP"],
                    "number_of_pages": 401,
                    "subject_classification": [
                        {"value": "519.226", "schema": "UDC"}
                    ],
                    "languages": ["en"],
                    "title": "Bayesian networks in fault diagnosis",
                    "alternative_titles": [
                        {
                            "value": "practice and application",
                            "type": "SUBTITLE",
                        }
                    ],
                    "legacy_recid": 2654497,
                    "isbns": [
                        {
                            "medium": "print version, hardback",
                            "value": "9789813271487",
                        }
                    ],
                    "authors": [
                        {"role": "editor", "full_name": "Cai, Baoping"},
                        {"role": "editor", "full_name": "Liu, Yonghong"},
                        {"role": "editor", "full_name": "Hu, Jinqiu"},
                        {"role": "editor", "full_name": "Liu, Zengkai"},
                        {"role": "editor", "full_name": "Wu, Shengnan"},
                        {"role": "editor", "full_name": "Ji, Renjie"},
                    ],
                    "original_source": None,
                    "external_system_identifiers": [
                        {"value": "90.20.00.192.6", "schema": "SCEM"}
                    ],
                    "$schema": {
                        "$ref": "records/books/book/book-v.0.0.1.json"
                    },
                    "document_type": "BOOK",
                    "imprints": [
                        {
                            "date": "2019",
                            "publisher": "World Scientific",
                            "place": "Singapore",
                        }
                    ],
                },
            )


def test_keywords(app):
    """Test public notes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="653" ind1="1" ind2=" ">
                <subfield code="g">PACS</subfield>
                <subfield code="a">Keyword Name 1</subfield>
            </datafield>
            """,
            {
                "keywords": [
                    {"value": "Keyword Name 1", "source": "PACS"},
                ],
            },
        )


def test_volume_barcodes(app):
    """Test volume barcodes (088__)."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Mathematische Methoden der Physik</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="x">80-1209-8</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="x">B00004172</subfield>
            </datafield>
            """,
            dict(
                title="Mathematische Methoden der Physik",
                _migration={
                    **get_helper_dict(),
                    **dict(
                        volumes=[
                            dict(barcode="80-1209-8", volume="1"),
                            dict(barcode="B00004172", volume="1"),
                        ],
                    ),
                },
            ),
        )


def test_conference_info_multiple_series_number(app):
    """Test conference info with multiple series numbers."""
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="111" ind1=" " ind2=" ">
                    <subfield code="9">20150708</subfield>
                    <subfield code="a">
                    3rd Singularity Theory Meeting of Northeast region & the Brazil-Mexico 2nd Meeting on Singularities
                    </subfield>
                    <subfield code="c">Salvador, Brazil</subfield>
                    <subfield code="d">8 - 11 & 13 - 17 Jul 2015</subfield>
                    <subfield code="f">2015</subfield>
                    <subfield code="g">salvador20150708</subfield>
                    <subfield code="n">3</subfield>
                    <subfield code="n">2</subfield>
                    <subfield code="w">BR</subfield>
                    <subfield code="z">20150717</subfield>
                </datafield>
                """,
                dict(),
            )


def test_open_access(app):
    """Test public notes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="r">x</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(),
                    "eitems_open_access": True,
                },
            },
        )
