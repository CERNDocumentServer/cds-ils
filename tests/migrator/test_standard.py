# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Standard fields tests."""

from __future__ import absolute_import, print_function, unicode_literals

from cds_dojson.marc21.utils import create_record

from cds_ils.importer.providers.cds.cds import get_helper_dict
from cds_ils.importer.providers.cds.models.standard import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    blob = create_record(marcxml.format(marcxml_body))
    model._default_fields = {"_migration": {**get_helper_dict()}}

    record = model.do(blob, ignore_missing=False)
    expected = {"_migration": {**get_helper_dict()}}
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
                        "language": "fr",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "fr",
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
                        "language": "fr",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "fr",
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
                        "language": "fr",
                    },
                    {
                        "type": "TRANSLATED_SUBTITLE",
                        "value": """part 15: guidance on the preservation and handling of sludge""",
                        "language": "fr",
                    },
                ],
            },
        )
