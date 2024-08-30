# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Standard fields tests."""

from cds_dojson.marc21.utils import create_record
from flask import current_app

from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.models.standard import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    blob = create_record(marcxml.format(marcxml_body))
    model._default_fields = {"_migration": {**get_helper_dict(record_type="document")}}

    record = model.do(blob, ignore_missing=False)
    expected = {"_migration": {**get_helper_dict(record_type="document")}}
    expected.update(**json_body)
    assert record == expected


def test_title(app):
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
                    {"value": "les règles de l'ICC", "type": "SUBTITLE"},
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            """,
            {
                "document_type": "STANDARD",
                "title": "Test",
                "alternative_titles": [
                    {"value": "Subtitle", "type": "SUBTITLE"},
                    {
                        "value": "Water quality — sampling",
                        "type": "TRANSLATED_TITLE",
                        "language": "FRA",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "FRA",
                    },
                ],
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">373 p</subfield>
            </datafield>
            """,
            {
                "document_type": "STANDARD",
                "title": "Test",
                "alternative_titles": [
                    {"value": "Subtitle", "type": "SUBTITLE"},
                    {
                        "value": "Water quality — sampling",
                        "type": "TRANSLATED_TITLE",
                        "language": "FRA",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "FRA",
                    },
                ],
                "number_of_pages": "373",
            },
        )
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">STANDARD</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Test</subfield>
                <subfield code="b">Subtitle</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">Water quality — sampling</subfield>
                <subfield code="b">
                part 15: guidance on the preservation and handling of sludge
            </subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">mult. p</subfield>
            </datafield>
            """,
            {
                "document_type": "STANDARD",
                "title": "Test",
                "alternative_titles": [
                    {"value": "Subtitle", "type": "SUBTITLE"},
                    {
                        "value": "Water quality — sampling",
                        "type": "TRANSLATED_TITLE",
                        "language": "FRA",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "FRA",
                    },
                ],
            },
        )


def test_publication_info(app):
    """Test publication info."""
    with app.app_context():
        host = current_app.config["SPA_HOST"]
        check_transformation(
            """
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="b">2155631</subfield>
                <subfield code="n">genoa20160330</subfield>
                <subfield code="k">1</subfield>
            </datafield>
            """,
            {
                "_migration": {
                    **get_helper_dict(record_type="document"),
                },
                "urls": [
                    {"value": f"{host}/legacy/2155631", "description": "is chapter of"}
                ],
                "publication_info": [
                    {
                        "pages": "1",
                    }
                ],
            },
        )


def test_subject_classification(app):
    """Test subject classification."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="c">25040.40</subfield>
            </datafield>
            """,
            {"subjects": [{"value": "25040.40", "scheme": "ICS"}]},
        )
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="c">13.75.Jz</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="c">13.60.Rj</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="c">14.20.Jn</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="c">25.80.Nv</subfield>
            </datafield>
            """,
            {
                "subjects": [
                    {"value": "13.75.Jz", "scheme": "ICS"},
                    {"value": "13.60.Rj", "scheme": "ICS"},
                    {"value": "14.20.Jn", "scheme": "ICS"},
                    {"value": "25.80.Nv", "scheme": "ICS"},
                ]
            },
        )
