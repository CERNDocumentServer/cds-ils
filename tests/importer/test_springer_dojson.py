import os

from cds_dojson.marc21.utils import create_record

from cds_ils.importer.providers.springer.springer import model

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


def test_springer_transformation(app):
    """Test springer record import translation."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "springer_record.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        check_transformation(
            example,
            {
                "_eitem": {
                    "internal_note": "Physics and Astronomy (R0) "
                    "(SpringerNature-43715)",
                    "urls": [
                        {
                            "description": "E-book by Springer",
                            "value": "https://doi.org/10.1007/b100336",
                        }
                    ],
                },
                "provider_recid": "978-0-306-47915-1",
                "_serial": [
                    {
                        "title": "Advances in Nuclear Physics ;",
                        "volume": "26",
                    }
                ],
                "abstract": "The four articles ...",
                "agency_code": "DE-He213",
                "alternative_titles": [
                    {"type": "SUBTITLE", "value": "Volume 26 /"}
                ],
                "alternative_identifiers": [
                    {"scheme": "SPRINGER", "value": "978-0-306-47915-1"}
                ],
                "authors": [
                    {"full_name": "Negele, J.W.", "roles": ["EDITOR"]},
                    {"full_name": "Vogt, Erich W.", "roles": ["EDITOR"]},
                ],
                "document_type": "BOOK",
                "edition": "1st ed. 2001.",
                "identifiers": [
                    {"scheme": "ISBN", "value": "9780306479151"},
                    {"scheme": "ISBN", "value": "9780306479151X"},
                ],
                "imprint": {
                    "date": "2001.",
                    "place": "New York, NY :",
                    "publisher": "Springer US :, Imprint: Springer,",
                },
                "keywords": [
                    {"source": "SPR", "value": "Nuclear physics."},
                    {"source": "SPR", "value": "Heavy ions."},
                    {
                        "source": "SPR",
                        "value": "Nuclear Physics, Heavy Ions, Hadrons.",
                    },
                ],
                "number_of_pages": "386",
                "publication_year": "2001.",
                "subjects": [
                    {"scheme": "LoC", "value": "QC770-798"},
                    {"scheme": "LoC", "value": "QC702.7.H42"},
                    {"scheme": "Dewey", "value": "539.7092"},
                ],
                "table_of_content": [
                    "The Spin Structure of the Nucleon",
                    "Liquid-Gas Phase Transition in Nuclear "
                    "Multifragmentation",
                    "High Spin Properties of Atomic Nuclei",
                    "The Deuteron: Structure and Form Factors.",
                ],
                "title": "Advances in Nuclear Physics",
            },
        )
