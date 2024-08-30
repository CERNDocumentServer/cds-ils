# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
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

"""Journal fields tests."""

import pytest
from cds_dojson.marc21.utils import create_record

from cds_ils.importer.errors import UnexpectedValue
from cds_ils.importer.providers.cds.models.journal import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    model._default_fields = {
        "_migration": {
            "is_multipart": False,
            "has_related": False,
            "related": [],
            "record_type": "journal",
            "volumes": [],
        }
    }
    record = model.do(blob, ignore_missing=False)

    expected = {
        "_migration": {
            "is_multipart": False,
            "has_related": False,
            "related": [],
            "record_type": "journal",
            "volumes": [],
        },
    }

    expected.update(**json_body)
    assert record == expected


def test_title(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Radioengineering</subfield>
                <subfield code="b">
                Proceedings of Czech and Slovak Technical Universities
                </subfield>
            </datafield>
                        """,
            {
                "title": "Radioengineering",
                "alternative_titles": [
                    {
                        "value": "Proceedings of Czech and Slovak Technical Universities",
                        "type": "SUBTITLE",
                    },
                ],
            },
        )


def test_alternative_titles(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">
                Recherche Coopérative sur Programme no 25
                </subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2="3">
                <subfield code="a">
                Les rencontres physiciens-mathématiciens de Strasbourg
                </subfield>
            </datafield>
            """,
            {
                "title": "Recherche Coopérative sur Programme no 25",
                "alternative_titles": [
                    {
                        "value": "Les rencontres physiciens-mathématiciens de Strasbourg",
                        "type": "ALTERNATIVE_TITLE",
                    },
                ],
            },
        )


def test_abbreviated_title(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="210" ind1=" " ind2=" ">
                <subfield code="a">Bull. CERN Comm.</subfield>
            </datafield>
            """,
            {
                "alternative_titles": [
                    {"type": "ABBREVIATION", "value": "Bull. CERN Comm."}
                ]
            },
        )


def test_identifiers(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="022" ind1=" " ind2=" ">
                <subfield code="a">1805-9600</subfield>
                <subfield code="b">online</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "scheme": "ISSN",
                        "value": "1805-9600",
                        "material": "DIGITAL",
                    }
                ],
            },
        )


def test_internal_notes(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="937" ind1=" " ind2=" ">
                <subfield code="a">Online archives purchased 2014</subfield>
            </datafield>
            """,
            {
                "internal_notes": [{"value": "Online archives purchased 2014"}],
            },
        )


def test_note(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="935" ind1=" " ind2=" ">
                <subfield code="a">
                The reports are catalogued individually and retrievable in the catalogue.
                </subfield>
            </datafield>
            """,
            {
                "note": "The reports are catalogued individually and retrievable in the catalogue.",
            },
        )


def test_publisher(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="933" ind1=" " ind2=" ">
                <subfield code="a">Bethesda, MD</subfield>
                <subfield code="b">
                National Council on Radiation Protection and Measurements
                </subfield>
            </datafield>
            """,
            {
                "publisher": "National Council on Radiation Protection and Measurements",
            },
        )


def test_languages(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">eng</subfield>
            </datafield>
            """,
            {
                "languages": ["ENG"],
            },
        )


def test_access_urls(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2="1">
                <subfield code="3">some notes</subfield>
                <subfield code="u">https://url.cern.ch/journal</subfield>
                <subfield code="x">8</subfield>
                <subfield code="z">some text</subfield>
            </datafield>
            """,
            {
                "access_urls": [
                    {
                        "access_restriction": ["RESTRICTED_PACKAGE_DEAL"],
                        "description": "some notes (some text)",
                        "value": "https://url.cern.ch/journal",
                        "login_required": False,
                        "open_access": False,
                    },
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2="1">
                <subfield code="3">some notes</subfield>
                <subfield code="u">https://url.cern.ch/journal</subfield>
                <subfield code="x">6</subfield>
            </datafield>
            """,
            {
                "access_urls": [
                    {
                        "access_restriction": ["OPEN_ACCESS"],
                        "description": "some notes",
                        "value": "https://url.cern.ch/journal",
                        "login_required": False,
                        "open_access": True,
                    },
                ],
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="856" ind1="4" ind2="1">
                    <subfield code="3">some notes</subfield>
                    <subfield code="u">https://ezproxy.cern.ch/login?url=https://url.cern.ch/journal</subfield>
                    <subfield code="x">8</subfield>
                    <subfield code="z">some text</subfield>
                </datafield>
                <datafield tag="856" ind1="4" ind2="1">
                    <subfield code="3">some other notes</subfield>
                    <subfield code="u">https://url.cern.ch/serial</subfield>
                    <subfield code="x">4</subfield>
                    <subfield code="z">some other text</subfield>
                </datafield>
                """,
                {
                    "access_urls": [
                        {
                            "access_restriction": ["RESTRICTED_PACKAGE_DEAL"],
                            "description": "some text",
                            "login_required": True,
                            "value": "https://url.cern.ch/journal",
                        },
                        {
                            "access_restriction": [None],
                            "description": "some other text",
                            "login_required": False,
                            "value": "https://url.cern.ch/serial",
                        },
                    ],
                },
            )


def test_urls(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2="2">
                <subfield code="u">https://url.cern.ch/journal</subfield>
                <subfield code="y">some text</subfield>
            </datafield>
            """,
            {
                "urls": [
                    {
                        "description": "some text",
                        "value": "https://url.cern.ch/journal",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2="1">
                <subfield code="3">v 1 (1992) -</subfield>
                <subfield code="u">
                https://www.radioeng.cz/search.htm
                </subfield>
                <subfield code="x">789</subfield>
                <subfield code="z">tada</subfield>
            </datafield>
            """,
            {
                "access_urls": [
                    {
                        "access_restriction": [
                            "RESTRICTED_PERPETUAL_ACCESS_BACKFILES",
                            "RESTRICTED_PACKAGE_DEAL",
                            "RESTRICTED_UNDEFINED",
                        ],
                        "description": "v 1 (1992) - (tada)",
                        "value": "https://www.radioeng.cz/search.htm",
                        "login_required": False,
                        "open_access": False,
                    },
                ],
            },
        )


def test_relation_migration(app):
    with app.app_context():
        check_transformation(
            """
                <datafield tag="787" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="x">language</subfield>
                    <subfield code="w">7483924</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "record_type": "journal",
                    "volumes": [],
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "language",
                            "relation_description": None,
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
                <datafield tag="770" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="x">other</subfield>
                    <subfield code="w">7483924</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "record_type": "journal",
                    "volumes": [],
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "other",
                            "relation_description": "Random text",
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
                <datafield tag="772" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="w">7483924</subfield>
                    <subfield code="x">other</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "record_type": "journal",
                    "volumes": [],
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "other",
                            "relation_description": "Random text",
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
                <datafield tag="780" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="w">7483924</subfield>
                    <subfield code="x">sequence</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "has_related": True,
                    "record_type": "journal",
                    "volumes": [],
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "sequence",
                            "sequence_order": "next",
                            "relation_description": None,
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
                <datafield tag="785" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="w">7483924</subfield>
                    <subfield code="x">sequence</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "has_related": True,
                    "record_type": "journal",
                    "volumes": [],
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "sequence",
                            "sequence_order": "previous",
                            "relation_description": None,
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
                <datafield tag="785" ind1=" " ind2=" ">
                    <subfield code="i">Split into</subfield>
                    <subfield code="t">Book1</subfield>
                    <subfield code="w">903671</subfield>
                    <subfield code="x">sequence</subfield>
                </datafield>
                <datafield tag="785" ind1=" " ind2=" ">
                    <subfield code="i">Split into</subfield>
                    <subfield code="t">Book2</subfield>
                    <subfield code="w"> 903672</subfield>
                    <subfield code="x">sequence</subfield>
                </datafield>
                """,
            {
                "_migration": {
                    "is_multipart": False,
                    "has_related": True,
                    "record_type": "journal",
                    "volumes": [],
                    "related": [
                        {
                            "related_recid": "903671",
                            "relation_type": "sequence",
                            "sequence_order": "previous",
                            "relation_description": None,
                        },
                        {
                            "related_recid": "903672",
                            "relation_type": "sequence",
                            "sequence_order": "previous",
                            "relation_description": None,
                        },
                    ],
                },
            },
        )


def test_physical_description(app):
    """Test medium."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">1 CD-ROM suppl</subfield>
                <subfield code="x">Phys.Desc.</subfield>
            </datafield>
            """,
            {
                "physical_description": "1 CD-ROM suppl",
            },
        )
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 1 CD-ROM suppl</subfield>
                <subfield code="x">Phys.desc</subfield>
            </datafield>
            """,
            {
                "physical_description": "2 v. ; 1 CD-ROM suppl",
            },
        )


def test_electronic_volumes_description(app):
    """Test electronic volumes description."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="362" ind1=" " ind2=" ">
                <subfield code="a">v 1 (1992) -</subfield>
            </datafield>
            """,
            {
                "note": "Dates of publication: v 1 (1992) -",
            },
        )
        check_transformation(
            """
            <datafield tag="362" ind1=" " ind2=" ">
                <subfield code="a">v 23 (1960) - v 64 (2002) ; v 70 (2008) -</subfield>
            </datafield>
            """,
            {
                "note": "Dates of publication: v 23 (1960) - v 64 (2002) ; v 70 (2008) -",
            },
        )


def test_physical_volumes_(app):
    """Test physical volumes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="866" ind1=" " ind2=" ">
                <subfield code="a">2017/2018 -</subfield>
                <subfield code="b">DE2</subfield>
                <subfield code="g">current</subfield>
                <subfield code="x">1</subfield>
            </datafield>
            """,
            {
                "physical_volumes": [
                    {
                        "description": "2017/2018 -",
                        "location": "DE2",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="866" ind1=" " ind2=" ">
                <subfield code="a">v 98 (2020) -</subfield>
                <subfield code="b">C</subfield>
                <subfield code="g">current</subfield>
                <subfield code="x">1</subfield>
            </datafield>
            <datafield tag="866" ind1=" " ind2=" ">
                <subfield code="a">v 92 no 7/8 (2014) - v 97 (2019)</subfield>
                <subfield code="b">DE2</subfield>
                <subfield code="g">current</subfield>
                <subfield code="x">1</subfield>
            </datafield>
            """,
            {
                "physical_volumes": [
                    {
                        "description": "v 98 (2020) -",
                        "location": "C",
                    },
                    {
                        "description": "v 92 no 7/8 (2014) - v 97 (2019)",
                        "location": "DE2",
                    },
                ],
            },
        )


def test_created(app):
    """Test physical volumes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="961" ind1=" " ind2=" ">
                <subfield code="c">20110222</subfield>
                <subfield code="h">1256</subfield>
                <subfield code="l">CER01</subfield>
                <subfield code="x">19920121</subfield>
            </datafield>
            """,
            {"_created": "1992-01-21"},
        )
