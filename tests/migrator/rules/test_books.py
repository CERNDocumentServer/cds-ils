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

import datetime

import pytest
from cds_dojson.marc21.utils import create_record
from dojson.errors import MissingRule

from cds_ils.importer.errors import (
    ManualImportRequired,
    MissingRequiredField,
    UnexpectedValue,
)
from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.models.document import model
from cds_ils.importer.providers.cds.rules.values_mapping import MATERIALS, mapping
from cds_ils.importer.providers.cds.utils import add_title_from_conference_info

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    model._default_fields = {"_migration": {**get_helper_dict(record_type="document")}}

    record = model.do(blob, ignore_missing=False)

    expected = {
        "_migration": {**get_helper_dict(record_type="document")},
    }

    expected.update(**json_body)
    assert record == expected


def test_conference_info_as_title(app):
    """Test title from conference info."""

    # if title rule is missing
    marcxml_body = """
            <datafield tag="111" ind1=" " ind2=" ">
                <subfield code="9">20040621</subfield>
                <subfield code="a">The conference title</subfield>
                <subfield code="c">Bari, Italy</subfield>
                <subfield code="z">20040621</subfield>
            </datafield>
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">43</subfield>
            </datafield>
            """
    json_body = {
        "conference_info": [
            {
                "title": "The conference title",
                "place": "Bari, Italy",
                "dates": "2004-06-21 - 2004-06-21",
            }
        ],
        "document_type": "PROCEEDINGS",
        "_migration": {
            **get_helper_dict(record_type="document"),
            "conference_title": "The conference title",
        },
    }
    check_transformation(marcxml_body, json_body)
    data = {
        "_migration": {**get_helper_dict(record_type="document")},
    }
    data.update(**json_body)
    add_title_from_conference_info(data)
    assert data["title"] == "The conference title"

    # if title rule exists
    marcxml_body += """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">The actual title</subfield>
            </datafield>
            """

    json_body.update(
        {
            "title": "The actual title",
        }
    )
    check_transformation(marcxml_body, json_body)
    data = {
        "_migration": {**get_helper_dict(record_type="document")},
    }
    data.update(**json_body)
    add_title_from_conference_info(data)
    assert data["title"] == "The actual title"


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
            {"subjects": [{"value": "515.353", "scheme": "DEWEY"}]},
        )
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA76.642</subfield>
                <subfield code="b">XXXX</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "QA76.642", "scheme": "LOC"}]},
        )
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2=" ">
                <subfield code="a">QA76.642</subfield>
                <subfield code="b">XXXX</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "QA76.642", "scheme": "LOC"}]},
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
                    {"value": "QA76.642", "scheme": "LOC"},
                    {"value": "005.275", "scheme": "DEWEY"},
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


def test_created_by_email(app):
    """Test acquisition email."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">john.doe@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "_email": "john.doe@cern.ch",
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
                <subfield code="f">john.doe@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "type": "user",
                    "_email": "john.doe@cern.ch",
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
            {
                "source": "SPR",
                "_created": "2017-01-01",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_internal_notes": "SPR201701",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR201701</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR2018</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">IEEE201901</subfield>
            </datafield>
            """,
            {
                "source": "SPR",
                "_created": "2017-01-01",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_internal_notes": "SPR201701; SPR2018; IEEE201901",
                },
                "internal_notes": [{"value": "SPR2018"}, {"value": "IEEE201901"}],
            },
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
                <subfield code="f">p.q@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "type": "user",
                    "_email": "p.q@cern.ch",
                },
                "source": "SPR",
                "_created": "2017-01-01",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_internal_notes": "SPR201701",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">202829</subfield>
            </datafield>
            """,
            {
                "_created": datetime.date.today().isoformat(),
                "created_by": {"type": "user"},
            },
        )
        # test earliest date
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
                <subfield code="w">201729</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR201701</subfield>
            </datafield>
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">p.q@cern.ch</subfield>
            </datafield>
            """,
            {
                "created_by": {
                    "type": "user",
                    "_email": "p.q@cern.ch",
                },
                "source": "SPR",
                "_created": "2017-01-01",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_internal_notes": "SPR201701",
                },
            },
        )


def test_tags(app):
    """Test tags."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "tags": ["LEGAL_SERVICE_LIBRARY"],
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "tags": ["LEGAL_SERVICE_LIBRARY"],
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """,
            {
                "tags": ["LEGAL_SERVICE_LIBRARY"],
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBINTLAW</subfield>
            </datafield>
            """,
            {
                "tags": ["LEGSERLIBINTLAW"],
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                "tags": ["BOOKSHOP"],
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                "tags": ["BOOKSHOP"],
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBLEGRES</subfield>
            </datafield>
            """,
            {
                "tags": ["LEGSERLIBLEGRES"],
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOKSUGGESTION</subfield>
                <subfield code="b">DIDACTICLIBRARY</subfield>
            </datafield>
             <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="b">PAULISCIENTIFICBOOK</subfield>
            </datafield>
            """,
            {
                "tags": ["BOOK_SUGGESTION", "DIDACTIC_LIBRARY"],
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="b">DIDACTICLIBRARY</subfield>
            </datafield>
            """,
            {
                "tags": ["DIDACTIC_LIBRARY"],
            },
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="b">PAULISCIENTIFICBOOK</subfield>
            </datafield>
            """,
            {},
        )


def test_serial(app):
    """Test serial."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">DESIGN REPORT</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "has_serial": True,
                    "serials": [
                        {
                            "title": "DESIGN REPORT",
                            "volume": None,
                            "issn": None,
                        }
                    ],
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
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">virTScvyb</subfield>
            </datafield>
            """,
            {},
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="b">ENGLISH BOOK CLUB</subfield>
            </datafield>
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">21</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "tags": [],
                },
                "document_type": "BOOK",
            },
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
                "tags": ["LEGAL_SERVICE_LIBRARY"],
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
                "tags": ["LEGAL_SERVICE_LIBRARY"],
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
                    **get_helper_dict(record_type="document"),
                    "eitems_has_files": True,
                    "eitems_file_links": [
                        {
                            "url": {
                                "description": "Description",
                                "value": "http://cds.cern.ch/record/1393420/files/NF-EN-13480-2-AC6.pdf",
                            },
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">https://cds.cern.ch/record/12345/files/abc.pdf</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_files": True,
                    "eitems_file_links": [
                        {
                            "url": {
                                "value": "https://cds.cern.ch/record/12345/files/abc.pdf"
                            },
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
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_ebl": True,
                    "eitems_ebl": [
                        {
                            "url": {
                                "value": "https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560",
                                "description": "e-book",
                            },
                        }
                    ],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">https://learning.oreilly.com/library/view/-/9781118491300/?ar</subfield>
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_safari": True,
                    "eitems_safari": [
                        {
                            "url": {
                                "value": "https://learning.oreilly.com/library/view/-/9781118491300/?ar",
                                "description": "e-book",
                            },
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
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_proxy": True,
                    "eitems_proxy": [
                        {
                            "url": {
                                "value": "https://www.worldscientific.com/toc/rast/10",
                                "description": "e-book",
                            },
                            "open_access": False,
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
                <subfield code="y">e-book</subfield>
            </datafield>
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">
                https://learning.oreilly.com/library/view/-/9781118491300/?ar
                </subfield>
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_ebl": True,
                    "eitems_ebl": [
                        {
                            "url": {
                                "value": "https://cdsweb.cern.ch/auth.py?r=EBLIB_P_1139560",
                                "description": "e-book",
                            },
                        },
                    ],
                    "eitems_safari": [
                        {
                            "url": {
                                "value": "https://learning.oreilly.com/library/view/-/9781118491300/?ar",
                                "description": "e-book",
                            },
                        },
                    ],
                    "eitems_has_safari": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u"> https://learning.oreilly.com/library/view/-/9781119745228/?ar </subfield>
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_safari": [
                        {
                            "url": {
                                "value": "https://learning.oreilly.com/library/view/-/9781119745228/?ar",
                                "description": "e-book",
                            },
                        },
                    ],
                    "eitems_has_safari": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u"> https://external.com </subfield>
                <subfield code="y">e-book</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_external": [
                        {
                            "url": {
                                "value": "https://external.com",
                                "description": "e-book",
                            },
                            "open_access": False,
                        },
                    ],
                    "eitems_has_external": True,
                }
            },
        )
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
                <subfield code="u">google.com</subfield>
                <subfield code="y">description</subfield>
            </datafield>
            """,
            {
                "urls": [{"value": "google.com", "description": "description"}],
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
                <subfield code="k">ORCID:0000-0003-1346-5133</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">Seyfert, Paul</subfield>
                <subfield code="0">AUTHOR|(INSPIRE)INSPIRE-00341737</subfield>
                <subfield code="0">AUTHOR|(SzGeCERN)692828</subfield>
                <subfield code="0">AUTHOR|(CDS)2079441</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="m">paul.seyfert@cern.ch</subfield>
                <subfield code="9">#BEARD#</subfield>
                <subfield code="q">Hillman, Jonathan</subfield>
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
                        "type": "PERSON",
                        "alternative_names": ["Neubert, Matthias"],
                    },
                    {
                        "full_name": "Glashow, Sheldon Lee",
                        "roles": ["EDITOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Van Dam, Hendrik",
                        "roles": ["EDITOR"],
                        "type": "PERSON",
                        "identifiers": [
                            {"scheme": "ORCID", "value": "ORCID:0000-0003-1346-5133"}
                        ],
                    },
                    {
                        "full_name": "Seyfert, Paul",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                        "affiliations": [{"name": "CERN"}],
                        "alternative_names": ["Hillman, Jonathan"],
                        "identifiers": [
                            {
                                "scheme": "INSPIRE ID",
                                "value": "INSPIRE-00341737",
                            },
                        ],
                    },
                    {
                        "full_name": "John Doe",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                        "affiliations": [
                            {"name": "CERN"},
                            {"name": "Univ. Gent"},
                        ],
                    },
                    {
                        "full_name": "Jane Doe",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
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
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Glashow, Sheldon Lee",
                        "roles": ["EDITOR"],
                        "type": "PERSON",
                    },
                ],
                "other_authors": True,
            },
        )

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
            {
                "authors": [
                    {
                        "full_name": "Langrognat, B",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {"full_name": "Sauniere, J", "roles": ["AUTHOR"], "type": "PERSON"},
                ],
                "other_authors": True,
            },
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
            """,
            {
                "publication_info": [
                    {
                        "pages": "1692-1695",
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "journal_volume": "42",
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
            """,
            {
                "publication_info": [
                    {
                        "pages": "1692-1695",
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "journal_volume": "42",
                    }
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">PROCEEDINGS</subfield>
            </datafield>
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
            </datafield>
            """,
            {
                "document_type": "PROCEEDINGS",
                "publication_info": [{"note": "1692 numebrs text etc Random text"}],
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">PROCEEDINGS</subfield>
            </datafield>
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
                <subfield code="g">123456</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "pages": "1692-1695",
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "note": "1692 numebrs text etc Random text",
                    }
                ],
                "document_type": "PROCEEDINGS",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "has_journal": True,
                    "journal_record_legacy_recids": [
                        {"recid": "123456", "volume": None}
                    ],
                },
            },
        )
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">PROCEEDINGS</subfield>
            </datafield>
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
                <subfield code="g">123456</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "pages": "1692-1695",
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "note": "1692 numebrs text etc Random text",
                    }
                ],
                "document_type": "PROCEEDINGS",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "has_journal": True,
                    "journal_record_legacy_recids": [
                        {"recid": "123456", "volume": None}
                    ],
                },
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
                <subfield code="g">123456</subfield>
            </datafield>
            """,
            {
                "publication_info": [
                    {
                        "pages": "1692-",
                        "year": 2007,
                        "journal_title": "Radiat. Meas.",
                        "journal_issue": "10",
                        "note": "1692 numebrs text etc Random text",
                    }
                ],
                "document_type": "BOOK",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "has_journal": True,
                    "journal_record_legacy_recids": [
                        {"recid": "123456", "volume": None}
                    ],
                },
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
                    "standard_review_applicability": ["APPLICABLE"],
                    "standard_review_checkdate": "2019-12-01",
                    "standard_review_expert": "Expert ICS-25.160",
                },
            },
        )
        check_transformation(
            """
            <datafield tag="925" ind1=" " ind2=" ">
                <subfield code="i">no longer applicable</subfield>
                <subfield code="p">Expert ICS-25.160</subfield>
                <subfield code="v">withdrawn</subfield>
                <subfield code="z">Reviewed inAugust 2019</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "standard_review_applicability": ["NO_LONGER_APPLICABLE"],
                    "standard_review_standard_validity": "withdrawn",
                    "standard_review_checkdate": "2019-08-01",
                    "standard_review_expert": "Expert ICS-25.160",
                },
            },
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="925" ind1=" " ind2=" ">
                    <subfield code="i">no longer applicable</subfield>
                    <subfield code="p">Expert ICS-25.160</subfield>
                    <subfield code="v">withdrawn</subfield>
                    <subfield code="z">Reviewed in December 2019 123</subfield>
                </datafield>
                """,
                {
                    "extensions": {
                        "standard_review_applicability": "",
                        "standard_review_standard_validity": "withdrawn",
                        "standard_review_checkdate": "2019-12-01",
                        "standard_review_expert": "Expert ICS-25.160",
                    },
                },
            )
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN SPS</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN SPS</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            <datafield tag="925" ind1=" " ind2=" ">
                <subfield code="i">no longer applicable</subfield>
                <subfield code="p">Expert ICS-25.160</subfield>
                <subfield code="v">withdrawn</subfield>
                <subfield code="z">Reviewed in April 2019</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "unit_accelerator": "CERN SPS",
                    "unit_experiment": ["ATLAS", "CMS"],
                    "unit_project": ["FCC"],
                    "standard_review_applicability": ["NO_LONGER_APPLICABLE"],
                    "standard_review_standard_validity": "withdrawn",
                    "standard_review_checkdate": "2019-04-01",
                    "standard_review_expert": "Expert ICS-25.160",
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
                <subfield code="x">language</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "748392",
                            "relation_type": "language",
                            "relation_description": "Test text",
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
                        **get_helper_dict(record_type="document"),
                        "has_related": True,
                        "related": [
                            {
                                "related_recid": "7483924",
                                "relation_type": "other",
                                "relation_description": None,
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
                    **get_helper_dict(record_type="document"),
                    "has_related": True,
                    "related": [
                        {
                            "related_recid": "7483924",
                            "relation_type": "other",
                            "relation_description": None,
                        },
                        {
                            "related_recid": "748",
                            "relation_type": "other",
                            "relation_description": None,
                        },
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
                <subfield code="a">CERN SPS</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN SPS</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "unit_accelerator": "CERN SPS",
                    "unit_experiment": ["ATLAS", "CMS"],
                    "unit_project": ["FCC"],
                }
            },
        )
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN SPS</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">KEK</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">Fermilab</subfield>
                <subfield code="e">CMS</subfield>
                <subfield code="p">FCC</subfield>
            </datafield>
            """,
            {
                "extensions": {
                    "unit_accelerator": "CERN SPS; KEK; Fermilab",
                    "unit_experiment": ["ATLAS", "CMS"],
                    "unit_project": ["FCC"],
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
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "material": "DIGITAL",
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
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9780691090849",
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                    },
                ],
            },
        )
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
            {},
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
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "material": "DIGITAL",
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
                        "scheme": "ISBN",
                    },
                    {
                        "value": "9781630811051",
                        "material": "DIGITAL",
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
                            "material": "electronic version",
                            "scheme": "ISBN",
                        },
                        {
                            "value": "9781630811051",
                            "material": "electronic version",
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
                    {"value": "arXiv:1808.02335", "scheme": "ARXIV"}
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
                "identifiers": [{"value": "hep-th/9509119", "scheme": "REPORT_NUMBER"}],
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
                        "scheme": "ARXIV",
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
                        "scheme": "ARXIV",
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
                        "scheme": "REPORT_NUMBER",
                    },
                    {
                        "value": "ATL-COM-PHYS-2017",
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
                <subfield code="q">e-book</subfield>
                <subfield code="9">source</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "material": "DIGITAL",
                        "value": "10.1007/978-1-4613-0247-6",
                        "scheme": "DOI",
                    }
                ],
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_external": True,
                    "eitems_external": [
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.1007/978-1-4613-0247-6",
                            },
                            "open_access": False,
                        }
                    ],
                },
            },
        )
        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.3390/books978-3-03943-243-1</subfield>
                <subfield code="q">e-book (Open Access)</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {
                        "material": "DIGITAL",
                        "value": "10.3390/books978-3-03943-243-1",
                        "scheme": "DOI",
                    }
                ],
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_external": True,
                    "eitems_external": [
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.3390/books978-3-03943-243-1",
                            },
                            "open_access": True,
                        }
                    ],
                },
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
                <subfield code="9">Inspire</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {
                        "scheme": "INSPIRE",
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
                <subfield code="q">e-book</subfield>
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
                        "material": "DIGITAL",
                    },
                ],
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_external": True,
                    "eitems_external": [
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.1007/s00269-016-0862-1",
                            },
                            "open_access": False,
                        },
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.1103/PhysRevLett.121.052004",
                            },
                            "open_access": False,
                        },
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.1103/PhysRevLett.121.052004",
                            },
                            "open_access": False,
                        },
                    ],
                },
            },
        )
        check_transformation(
            """
            <datafield tag="036" ind1=" " ind2=" ">
                <subfield code="9">DLC</subfield>
                <subfield code="a">92074207</subfield>
            </datafield>
            """,
            # ignore DLC
            {
                # "alternative_identifiers": [
                #     {
                #         "scheme": "DLC",
                #         "value": "92074207",
                #     }
                # ],
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
                        "scheme": "ARXIV",
                        "value": "arXiv:1209.5665",
                    }
                ],
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
                    {"value": "arXiv:1209.5665", "scheme": "ARXIV"}
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math-phss</subfield>
            </datafield>
            """,
            {
                "alternative_identifiers": [
                    {"value": "arXiv:1209.5665", "scheme": "ARXIV"}
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
                "languages": ["ENG"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">english</subfield>
            </datafield>
            """,
            {
                "languages": ["ENG"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">fre</subfield>
            </datafield>
            """,
            {
                "languages": ["FRA"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">pl</subfield>
            </datafield>
            """,
            {
                "languages": ["POL"],
            },
        )
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">ger</subfield>
            </datafield>
            """,
            {
                "languages": ["DEU"],
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
                    "languages": ["DEU"],
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
                <subfield code="c">2013-01-15</subfield>
                <subfield code="g">2015</subfield>
            </datafield>
            """,
            {
                "publication_year": "2013",
                "imprint": {
                    "place": "Sydney",
                    "publisher": "Allen & Unwin",
                    "date": "2013-01-15",
                    "reprint": "2015",
                },
            },
        )
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
                    "date": "2013-01-01",
                    "reprint": "2015",
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
                "physical_description": "1 CD-ROM",
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
                "physical_description": "2 CD-ROM, 1 DVD, 1 VHS",
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
                            "id": "arXiv-nonexclusive-distrib-1.0",
                        }
                    },
                    {
                        "license": {
                            "id": "CC-BY-4.0",
                        },
                        "material": "preprint",
                    },
                    {
                        "license": {
                            "id": "CC-BY-4.0",
                        },
                        "material": "publication",
                        "internal_notes": "DAI/7161287",
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
                "conference_info": [
                    {
                        "title": """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                        "identifiers": [
                            {"scheme": "CERN", "value": "bari20040621"},
                        ],
                        "place": "Bari, Italy",
                        "dates": "2004-06-21 - 2004-06-21",
                        "series": "2",
                        "country": "ITA",
                    }
                ],
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "conference_title": """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                },
                "alternative_titles": [
                    {
                        "value": "SNGHEGE2004",
                        "type": "ALTERNATIVE_TITLE",
                    }
                ],
            },
        )
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
                <subfield code="x">SNGHEGE2004</subfield>
                <subfield code="w">IT</subfield>
                <subfield code="z">20040621</subfield>
            </datafield>
            <datafield tag="711" ind1=" " ind2=" ">
                <subfield code="a">SNGHEGE2004</subfield>
                <subfield code="x">acronym</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "conference_title": """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                },
                "conference_info": [
                    {
                        "identifiers": [
                            {"scheme": "CERN", "value": "bari20040621"},
                        ],
                        "title": """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                        "place": "Bari, Italy",
                        "dates": "2004-06-21 - 2004-06-21",
                        "series": "2",
                        "country": "ITA",
                        "acronym": "SNGHEGE2004",
                    }
                ],
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
                    "conference_info": [
                        {
                            "title": """2nd Workshop on Science with the New
                             Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                            "place": "Bari, Italy",
                            "identifiers": [
                                {
                                    "scheme": "CERN",
                                    "value": "bari20040621",
                                },
                            ],
                            "dates": "2004-06-21 - 2004-06-21",
                            "series": "2",
                            "country_code": "ITA",
                            "contact": "arantza.de.oyanguren.campos@cern.ch",
                        }
                    ]
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
                        "conference_info": [
                            {
                                "title": """2nd Workshop on Science with the New
                             Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                                "place": "Bari, Italy",
                                "cern_conference_code": "bari20040621",
                                "opening_date": "2004-06-21",
                                "series": "2",
                                "country_code": "ITA",
                                "closing_date": "2004-06-21",
                                "contact": "arantza.de.oyanguren.campos@cern.ch",
                            }
                        ],
                        "_migration": {
                            "conference_title": """2nd Workshop on Science with the New
                             Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                            "conference_place": "Bari, Italy",
                        },
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
                        "conference_info": [
                            {"contact": "arantza.de.oyanguren.campos@cern.ch"}
                        ]
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
                        "language": "ENG",
                        "type": "TRANSLATED_TITLE",
                    },
                    {
                        "value": "Subtitle/LHC",
                        "language": "ENG",
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
            {"note": """Translated from ... \nNo CD-ROM"""},
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
        check_transformation(
            """
            <datafield tag="505" ind1="0" ind2=" ">
                <subfield code="t">
                CONTENTS; PREFACE; CHAPTER 1  GENERALITIES ON DYNAMIC SYSTEMS AND MAPS; 1.1. Continuous Dynamic Systems and Discrete Dynamic Systems.; 1.2. Some Considerations on Maps and Some Definitions.
                </subfield>
            </datafield>
            <datafield tag="505" ind1="0" ind2=" ">
                <subfield code="t">
                1.8.1. Generalities.1.8.2. Basin boundary, singular points and the Schroeder's equation.; 1.8.3. One-dimensional noninveriible maps and chaotic behaviours. Generalization of Chebyshev's polynomials.; 1.8.4. One-dimensional noninvertible maps. Properties of generalized Chebyshev's polynomials.
                </subfield>
            </datafield>
            """,
            {
                "table_of_content": [
                    "CONTENTS",
                    "PREFACE",
                    "CHAPTER 1  GENERALITIES ON DYNAMIC SYSTEMS AND MAPS",
                    "1.1. Continuous Dynamic Systems and Discrete Dynamic Systems.",
                    "1.2. Some Considerations on Maps and Some Definitions.",
                    "1.8.1. Generalities.1.8.2. Basin boundary, singular points and the Schroeder's equation.",
                    "1.8.3. One-dimensional noninveriible maps and chaotic behaviours. Generalization of Chebyshev's polynomials.",
                    "1.8.4. One-dimensional noninvertible maps. Properties of generalized Chebyshev's polynomials.",
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
                    **get_helper_dict(record_type="document"),
                    "serials": [{"title": "Minutes", "issn": None, "volume": None}],
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
                    **get_helper_dict(record_type="document"),
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
                    **get_helper_dict(record_type="document"),
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
                    "subject_classification": [{"value": "519.226", "schema": "UDC"}],
                    "languages": ["ENG"],
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
                    "$schema": {"$ref": "records/books/book/book-v.0.0.1.json"},
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
                    **get_helper_dict(record_type="document"),
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
        check_transformation(
            """
            <datafield tag="111" ind1=" " ind2=" ">
                <subfield code="9">20150708</subfield>
                <subfield code="a">
                3rd Singularity Theory Meeting of Northeast region and the Brazil-Mexico 2nd Meeting on Singularities
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
            {
                "conference_info": [
                    {
                        "title": "3rd Singularity Theory Meeting of Northeast region and the Brazil-Mexico 2nd Meeting on Singularities",
                        "place": "Salvador, Brazil",
                        "country": "BRA",
                        "dates": "2015-07-08 - 2015-07-17",
                        "series": "3, 2",
                        "identifiers": [
                            {
                                "scheme": "CERN",
                                "value": "salvador20150708",
                            }
                        ],
                    }
                ],
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "conference_title": "3rd Singularity Theory Meeting of Northeast region and the Brazil-Mexico 2nd Meeting on Singularities",
                },
            },
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
                    **get_helper_dict(record_type="document"),
                    "eitems_open_access": False,
                },
            },
        ),
        check_transformation(
            """
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="r">Open Access</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_open_access": True,
                },
            },
        )


def test_record(app):
    """Test real record: https://cds.cern.ch/record/2749387/export/xm?ln=en"""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9789811590344</subfield>
                <subfield code="b">electronic version</subfield>
                <subfield code="u">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9789811590337</subfield>
                <subfield code="u">print version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9789811590351</subfield>
                <subfield code="u">print version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9789811590368</subfield>
                <subfield code="u">print version</subfield>
            </datafield>
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA313</subfield>
            </datafield>
            <datafield tag="082" ind1="0" ind2="4">
                <subfield code="2">23</subfield>
                <subfield code="a">515.39</subfield>
            </datafield>
            <datafield tag="082" ind1="0" ind2="4">
                <subfield code="2">23</subfield>
                <subfield code="a">515.48</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Nonlinear dynamics, chaos, and complexity</subfield>
                <subfield code="b">in memory of professor Valentin Afraimovich</subfield>
            </datafield>
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Nonlinear physical science</subfield>
                <subfield code="x">1867-8440</subfield>
            </datafield>
            <datafield tag="505" ind1="0" ind2=" ">
                <subfield code="a">Professor Valentin Afraimovich -- The need for more integration between machine learning and neuroscience. Quasiperiodic Route to Transient Chaos in Vibroimpact System -- Modeling Ensembles of Nonlinear Dynamic Systems in Ultrawideb and Active Wireless Direct Chaotic Networks -- Verification of Biomedical Processes with Anomalous Diffusion, Transport and Interaction of Species -- Chaos-based communication using isochronal synchronization: considerations about the synchronization manifold.</subfield>
            </datafield>
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">This book demonstrates how mathematical methods and techniques can be used in synergy and create a new way of looking at complex systems. It becomes clear nowadays that the standard (graph-based) network approach, in which observable events and transportation hubs are represented by nodes and relations between them are represented by edges, fails to describe the important properties of complex systems, capture the dependence between their scales, and anticipate their future developments. Therefore, authors in this book discuss the new generalized theories capable to describe a complex nexus of dependences in multi-level complex systems and to effectively engineer their important functions. The collection of works devoted to the memory of Professor Valentin Afraimovich introduces new concepts, methods, and applications in nonlinear dynamical systems covering physical problems and mathematical modelling relevant to molecular biology, genetics, neurosciences, artificial intelligence as well as classic problems in physics, machine learning, brain and urban dynamics. The book can be read by mathematicians, physicists, complex systems scientists, IT specialists, civil engineers, data scientists, urban planners, and even musicians (with some mathematical background). .</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">Physics and astronomy</subfield>
            </datafield>
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">eng</subfield>
            </datafield>
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR202101</subfield>
            </datafield>
            <datafield tag="653" ind1="1" ind2=" ">
                <subfield code="9">SPR</subfield>
                <subfield code="a">Vibration</subfield>
            </datafield>
            <datafield tag="653" ind1="1" ind2=" ">
                <subfield code="9">SPR</subfield>
                <subfield code="a">Dynamical systems</subfield>
            </datafield>
            <datafield tag="653" ind1="1" ind2=" ">
                <subfield code="9">SPR</subfield>
                <subfield code="a">Vibration, Dynamical Systems, Control</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Volchenkov, Dimitri</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="d">202101</subfield>
                <subfield code="e">SPR</subfield>
                <subfield code="s">n</subfield>
                <subfield code="w">202101</subfield>
            </datafield>
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">21</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1007/978-981-15-9034-4</subfield>
                <subfield code="q">e-book</subfield>
            </datafield>
            """,
            {
                "_created": "2021-01-04",
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "eitems_has_external": True,
                    "eitems_internal_notes": "SPR202101",
                    "eitems_external": [
                        {
                            "url": {
                                "description": "e-book",
                                "value": "http://dx.doi.org/10.1007/978-981-15-9034-4",
                            },
                            "open_access": False,
                        }
                    ],
                    "has_serial": True,
                    "serials": [
                        {
                            "issn": "1867-8440",
                            "title": "Nonlinear physical science",
                            "volume": None,
                        }
                    ],
                },
                "abstract": "This book demonstrates how mathematical methods "
                "and techniques can be used in synergy and create "
                "a new way of looking at complex systems. It "
                "becomes clear nowadays that the standard "
                "(graph-based) network approach, in which "
                "observable events and transportation hubs are "
                "represented by nodes and relations between them "
                "are represented by edges, fails to describe the "
                "important properties of complex systems, capture "
                "the dependence between their scales, and "
                "anticipate their future developments. Therefore, "
                "authors in this book discuss the new generalized "
                "theories capable to describe a complex nexus of "
                "dependences in multi-level complex systems and to"
                " effectively engineer their important functions. "
                "The collection of works devoted to the memory of "
                "Professor Valentin Afraimovich introduces new "
                "concepts, methods, and applications in nonlinear "
                "dynamical systems covering physical problems and "
                "mathematical modelling relevant to molecular "
                "biology, genetics, neurosciences, artificial "
                "intelligence as well as classic problems in "
                "physics, machine learning, brain and urban "
                "dynamics. The book can be read by mathematicians,"
                " physicists, complex systems scientists, IT "
                "specialists, civil engineers, data scientists, "
                "urban planners, and even musicians (with some "
                "mathematical background). .",
                "alternative_titles": [
                    {
                        "type": "SUBTITLE",
                        "value": "in memory of professor Valentin Afraimovich",
                    }
                ],
                "authors": [
                    {
                        "full_name": "Volchenkov, Dimitri",
                        "roles": ["EDITOR"],
                        "type": "PERSON",
                    }
                ],
                "created_by": {"type": "batchuploader"},
                "document_type": "BOOK",
                "identifiers": [
                    {"material": "DIGITAL", "scheme": "ISBN", "value": "9789811590344"},
                    {
                        "material": "PRINT_VERSION",
                        "scheme": "ISBN",
                        "value": "9789811590337",
                    },
                    {
                        "material": "PRINT_VERSION",
                        "scheme": "ISBN",
                        "value": "9789811590351",
                    },
                    {
                        "material": "PRINT_VERSION",
                        "scheme": "ISBN",
                        "value": "9789811590368",
                    },
                    {
                        "material": "DIGITAL",
                        "scheme": "DOI",
                        "value": "10.1007/978-981-15-9034-4",
                    },
                ],
                "internal_notes": [{"value": "Physics and astronomy"}],
                "keywords": [
                    {"source": "SPR", "value": "Vibration"},
                    {"source": "SPR", "value": "Dynamical systems"},
                    {"source": "SPR", "value": "Vibration, Dynamical Systems, Control"},
                ],
                "languages": ["ENG"],
                "source": "SPR",
                "subjects": [
                    {"scheme": "LOC", "value": "QA313"},
                    {"scheme": "DEWEY", "value": "515.39"},
                    {"scheme": "DEWEY", "value": "515.48"},
                ],
                "table_of_content": [
                    "Professor Valentin Afraimovich",
                    "The need for more integration between "
                    "machine learning and neuroscience. "
                    "Quasiperiodic Route to Transient Chaos "
                    "in Vibroimpact System",
                    "Modeling Ensembles of Nonlinear Dynamic "
                    "Systems in Ultrawideb and Active "
                    "Wireless Direct Chaotic Networks",
                    "Verification of Biomedical Processes "
                    "with Anomalous Diffusion, Transport"
                    " and Interaction of Species",
                    "Chaos-based communication using "
                    "isochronal synchronization: "
                    "considerations about the "
                    "synchronization manifold.",
                ],
                "title": "Nonlinear dynamics, chaos, and complexity",
            },
        )


def test_medium(app):
    """Test medium."""
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="340" ind1=" " ind2=" ">
                    <subfield code="a">WHATEVER</subfield>
                </datafield>
                """,
                {
                    "_migration": {
                        **get_helper_dict(record_type="document"),
                    },
                },
            )
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="a">DVD video</subfield>
                <subfield code="x">CM-B00065102</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "item_medium": [
                        {
                            "barcode": "CM-B00065102",
                            "medium": "DVD",
                        }
                    ],
                    "has_medium": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="a">paper</subfield>
                <subfield code="x">CM-B00062302</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "item_medium": [
                        {
                            "barcode": "CM-B00062302",
                            "medium": "PAPER",
                        }
                    ],
                    "has_medium": True,
                },
            },
        )
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="a">VHS</subfield>
                <subfield code="x">CM-B00063302</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "item_medium": [
                        {
                            "barcode": "CM-B00063302",
                            "medium": "VHS",
                        }
                    ],
                    "has_medium": True,
                },
            },
        )
        # https://cds.cern.ch/record/1058314/export/xm?ln=en
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="a">CD-ROM</subfield>
                <subfield code="x">CM-P00096545</subfield>
                <subfield code="x">CM-B00048086</subfield>
                <subfield code="x">CM-B00048085</subfield>
                <subfield code="x">CM-B00048085</subfield>
                <subfield code="x">CM-B00048083</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                    "item_medium": [
                        {
                            "barcode": "CM-P00096545",
                            "medium": "CDROM",
                        },
                        {
                            "barcode": "CM-B00048086",
                            "medium": "CDROM",
                        },
                        {
                            "barcode": "CM-B00048085",
                            "medium": "CDROM",
                        },
                        {
                            "barcode": "CM-B00048083",
                            "medium": "CDROM",
                        },
                    ],
                    "has_medium": True,
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
