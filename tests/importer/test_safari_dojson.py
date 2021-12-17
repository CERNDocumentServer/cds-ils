import os

from cds_dojson.marc21.utils import create_record

from cds_ils.importer.providers.safari.safari import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    record = {}
    record.update(**model.do(blob, ignore_missing=True))

    expected = {}
    expected.update(**json_body)

    assert record == expected


def test_safari_transformation(app):
    """Test safari record json translation."""

    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_record.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        check_transformation(
            example,
            {
                "document_type": "BOOK",
                "_eitem": {
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com"
                                     "/library/view/-/9780814415467/?ar",
                        }
                    ]
                },
                "abstract": "A complete tool kit for handling "
                            "disciplinary problems in a "
                            "fair, responsible, and legally defensible way.",
                "agency_code": "CaSebORM",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "9780814415467"}
                ],
                "alternative_titles": [
                    {
                        "type": "SUBTITLE",
                        "value": "A Guide to Progressive Discipline and "
                                 "Termination",
                    }
                ],
                "authors": [
                    {"full_name": "Falcone, Paul",
                     "roles": ["AUTHOR"],
                     "type": "PERSON",
                     }
                ],
                "edition": "2nd",
                "identifiers": [{'material': 'PRINT_VERSION',
                                 'scheme': 'ISBN',
                                 'value': '9780814415467'},
                                {'material': 'PRINT_VERSION',
                                 'scheme': 'ISBN',
                                 'value': '9780814415474'},
                                {'material': 'DIGITAL',
                                 'scheme': 'ISBN',
                                 'value': '9780814415467'}],
                "languages": ["ENG"],
                "provider_recid": "9780814415467",
                "imprint": {"publisher": "AMACOM",
                            "place": "S.L."},
                "number_of_pages": "1",
                "publication_year": "2010",
                "title": "101 Sample Write-Ups for "
                         "Documenting Employee Performance Problems",
            },
        )
