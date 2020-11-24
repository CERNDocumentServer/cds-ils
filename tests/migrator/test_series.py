# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""CDS-ILS Test series fields."""

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from cds_dojson.marc21.utils import create_record
from dojson.errors import MissingRule

from cds_ils.importer.errors import MissingRequiredField, UnexpectedValue
from cds_ils.importer.providers.cds.models.multipart import \
    model as multipart_model
from cds_ils.importer.providers.cds.models.serial import model as serial_model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body, model=None):
    """Check transformation."""
    if model == multipart_model:
        model._default_fields = {
            "_migration": {"record_type": "multipart", "volumes": []},
            "mode_of_issuance": "MULTIPART_MONOGRAPH",
        }
    else:
        model._default_fields = {
            "_migration": {"record_type": "serial", "children": []},
            "mode_of_issuance": "SERIAL",
        }
    blob = create_record(marcxml.format(marcxml_body))
    record = model.do(blob, ignore_missing=False)
    expected = {}
    expected.update(**json_body)
    assert record == expected


def test_serial(app):
    """Test serials."""

    with app.app_context():
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">
                Esl and applied linguistics professional
                </subfield>
            </datafield>
            """,
            {
                "title": ["Esl and applied linguistics professional"],
                "mode_of_issuance": "SERIAL",
                "_migration": {"record_type": "serial", "children": []},
            },
            serial_model,
        )

        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">
                Springerbriefs in history of science and technology
                </subfield>
                <subfield code="x">2211-4564</subfield>
            </datafield>
            """,
            {
                "title": [
                    "Springerbriefs in history" " of science and technology"
                ],
                "mode_of_issuance": "SERIAL",
                "identifiers": [{"scheme": "ISSN", "value": "2211-4564"}],
                "_migration": {"record_type": "serial", "children": []},
            },
            serial_model,
        )

        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">
                Springerbriefs in history of science and technology
                </subfield>
                <subfield code="x">2211-4564</subfield>
            </datafield>
            """,
            {
                "title": [
                    "Springerbriefs in history" " of science and technology"
                ],
                "mode_of_issuance": "SERIAL",
                "identifiers": [{"scheme": "ISSN", "value": "2211-4564"}],
                "_migration": {"record_type": "serial", "children": []},
            },
            serial_model,
        )

        with pytest.raises(MissingRule):
            check_transformation(
                """
                <datafield tag="490" ind1="1" ind2=" ">
                    <subfield code="a"
                    >Modesty Blaise / Peter O'Donnell
                    </subfield>
                </datafield>
                """,
                {
                    "title": [
                        "Springerbriefs in history"
                        " of science and technology"
                    ],
                    "_migration": {"record_type": "serial", "children": []},
                },
                serial_model,
            )


def test_monograph(app):
    """Test monographs."""

    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="p">
                Introduzione alla fisica meccanica
                </subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                "title": "La fisica di Amaldi",
                "alternative_titles": [
                    {
                        "value": "idee ed esperimenti : con CD-ROM",
                        "type": "SUBTITLE",
                    }
                ],
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "number_of_volumes": "2",
                "_migration": {
                    "record_type": "multipart",
                    "volumes": [
                        {
                            "title": "Introduzione alla fisica meccanica",
                            "volume": 1,
                        },
                        {"title": "Termologia, onde, relatività", "volume": 2},
                    ],
                },
            },
            multipart_model,
        )

        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                "title": "La fisica di Amaldi",
                "alternative_titles": [
                    {
                        "value": "idee ed esperimenti : con CD-ROM",
                        "type": "SUBTITLE",
                    }
                ],
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "number_of_volumes": "2",
                "_migration": {
                    "record_type": "multipart",
                    "volumes": [
                        {"title": "Termologia, onde, relatività", "volume": 2}
                    ],
                },
            },
            multipart_model,
        )

        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 p ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                "title": "La fisica di Amaldi",
                "alternative_titles": [
                    {
                        "value": "idee ed esperimenti : con CD-ROM",
                        "type": "SUBTITLE",
                    }
                ],
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "_migration": {
                    "record_type": "multipart",
                    "volumes": [
                        {"title": "Termologia, onde, relatività", "volume": 2}
                    ],
                },
            },
            multipart_model,
        )

        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">multi. p ; 2 CD-ROM suppl</subfield>
            </datafield>

            """,
            {
                "title": "La fisica di Amaldi",
                "alternative_titles": [
                    {
                        "value": "idee ed esperimenti : con CD-ROM",
                        "type": "SUBTITLE",
                    }
                ],
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "_migration": {
                    "record_type": "multipart",
                    "volumes": [
                        {"title": "Termologia, onde, relatività", "volume": 2}
                    ],
                },
            },
            multipart_model,
        )

        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="245" ind1=" " ind2=" ">
                    <subfield code="a">La fisica di Amaldi</subfield>
                    <subfield code="b">
                    idee ed esperimenti : con CD-ROM
                    </subfield>
                </datafield>
                <datafield tag="246" ind1=" " ind2=" ">
                    <subfield code="a">v.2</subfield>
                    <subfield code="b">Termologia, onde, relatività</subfield>
                </datafield>
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
                </datafield>
                """,
                {
                    "title": "La fisica di Amaldi",
                    "alternative_titles": [
                        {
                            "value": "idee ed esperimenti : con CD-ROM",
                            "type": "SUBTITLE",
                        }
                    ],
                    "mode_of_issuance": "MULTIPART_MONOGRAPH",
                    "number_of_volumes": "2",
                    "_migration": {"record_type": "multipart", "volumes": []},
                },
                multipart_model,
            )

        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="246" ind1=" " ind2=" ">
                    <subfield code="n">v.2</subfield>
                    <subfield code="p">Termologia, onde, relatività</subfield>
                </datafield>
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
                </datafield>
                """,
                {
                    "title": "La fisica di Amaldi",
                    "alternative_titles": [
                        {
                            "value": "idee ed esperimenti : con CD-ROM",
                            "type": "SUBTITLE",
                        }
                    ],
                    "mode_of_issuance": "MULTIPART_MONOGRAPH",
                    "number_of_volumes": "2",
                    "_migration": {"record_type": "multipart", "volumes": []},
                },
                multipart_model,
            )


def test_monograph_migration(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052819</subfield>
                <subfield code="u">print version, paperback (v.3)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052818</subfield>
                <subfield code="u">print version, paperback (v.3)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052801</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052800</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052825</subfield>
                <subfield code="u">print version, paperback (set)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052795</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052797</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Wissenschaftliche Abhandlungen</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="p">1865-1874</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">1875-1881</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.3</subfield>
                <subfield code="p">1882-1905</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">3 v</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    "volumes": [
                        {
                            "volume": 3,
                            "isbn": "1108052819",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {
                            "volume": 3,
                            "isbn": "9781108052818",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {
                            "volume": 2,
                            "isbn": "9781108052801",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {
                            "volume": 2,
                            "isbn": "1108052800",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {
                            "volume": 1,
                            "isbn": "9781108052795",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {
                            "volume": 1,
                            "isbn": "1108052797",
                            "physical_description": "print version, paperback",
                            "is_electronic": False,
                        },
                        {"title": "1865-1874", "volume": 1},
                        {"title": "1875-1881", "volume": 2},
                        {"title": "1882-1905", "volume": 3},
                    ],
                    "record_type": "multipart",
                },
                "title": "Wissenschaftliche Abhandlungen",
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "number_of_volumes": "3",
                "identifiers": [{"scheme": "ISBN", "value": "9781108052825"}],
                "physical_description": "print version, paperback",
            },
            multipart_model,
        )


def test_monograph_invalid_volume_migration(app):
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808175366</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808247049</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808047038</subfield>
                <subfield code="u">
                print version, paperback (v.2, CD-ROM)
                </subfield>
                </datafield>
                """,
                {},
                multipart_model,
            )


def test_monograph_invalid_volume_migration_no_description(app):
    """Test invalid multipart volume (https://cds.cern.ch/record/287517)."""
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1560810726</subfield>
                <subfield code="u">v.13</subfield>
                </datafield>
                """,
                {},
                multipart_model,
            )


def test_monograph_with_electronic_isbns(app):
    """Test multipart monographs with electronic isbns."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631852</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631852</subfield>
                <subfield code="u">print version (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631879</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780817631857</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780817631871</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461239406</subfield>
                <subfield code="b">electronic version (v.2)</subfield>
                <subfield code="u">electronic version (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461251545</subfield>
                <subfield code="b">electronic version (v.1)</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461295891</subfield>
                <subfield code="u">print version (v.1)</subfield>
            </datafield>
            """,
            {
                "identifiers": [
                    {"scheme": "ISBN", "value": "0817631852"},
                    {"scheme": "ISBN", "value": "0817631879"},
                    {"scheme": "ISBN", "value": "9780817631857"},
                    {"scheme": "ISBN", "value": "9780817631871"},
                ],
                "mode_of_issuance": "MULTIPART_MONOGRAPH",
                "_migration": {
                    "record_type": "multipart",
                    "volumes": [
                        {
                            "is_electronic": False,
                            "physical_description": "print version",
                            "volume": 2,
                            "isbn": "0817631852",
                        },
                        {
                            "is_electronic": True,
                            "physical_description": "electronic version",
                            "volume": 2,
                            "isbn": "9781461239406",
                        },
                        {
                            "is_electronic": True,
                            "physical_description": "electronic version",
                            "volume": 1,
                            "isbn": "9781461251545",
                        },
                        {
                            "is_electronic": False,
                            "physical_description": "print version",
                            "volume": 1,
                            "isbn": "9781461295891",
                        },
                    ],
                },
            },
            multipart_model,
        )
