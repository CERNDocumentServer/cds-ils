import os

from cds_dojson.marc21.utils import create_record

from cds_ils.importer.providers.ebl.ebl import model

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


def test_ebl_transformation(app):
    """Test springer record import translation."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "ebl_record.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        check_transformation(
            example,
            {
                "_eitem": {
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://ebookcentral.proquest.com/lib/"
                            "cern/detail.action?docID=263817",
                        }
                    ],
                },
                "_serial": [{"title": "Condensed Matter Physics series"}],
                "provider_recid": "EBC263817",
                "document_type": "BOOK",
                "abstract": "IntroductionTheoryMagnetocaloric effect in the "
                "phase transition "
                "regionMethods of investigation of magnetocaloric "
                "propertiesMagnetocaloric effect in 3d metals and their "
                "alloysMagnetocaloric effect in amorphous "
                "materialsMagnetocaloric "
                "effect in rare earth metals and their alloysMagnetocaloric "
                "effect in intermetallic compounds with rare earth "
                "elementsMagnetocaloric effect in oxide "
                "compoundsMagnetocaloric "
                "effect in silicides and germanidesMagnetocaloric effect in "
                "nanosized materialsMagnetic refrigerationConclusions.",
                "agency_code": "MiAaPQ",
                "alternative_identifiers": [
                    {"scheme": "EBL", "value": "263817"},
                ],
                "authors": [
                    {
                        "full_name": "Tishin, A. M",
                        "type": "PERSON",
                        "roles": ["AUTHOR"],
                    },
                    {
                        "full_name": "Spichkin, Y. I",
                        "type": "PERSON",
                        "roles": ["AUTHOR"],
                    },
                    {
                        "full_name": "Tishin, A.M",
                        "type": "PERSON",
                        "roles": ["AUTHOR"],
                    },
                    {
                        "full_name": "Spichkin, Y.I",
                        "type": "PERSON",
                        "roles": ["AUTHOR"],
                    },
                ],
                "edition": "1st",
                "identifiers": [
                    {"scheme": "ISBN", "value": "9781420033373", "material": "DIGITAL"},
                    {
                        "scheme": "ISBN",
                        "value": "9780750309226",
                        "material": "PRINT_VERSION",
                    },
                ],
                "imprint": {
                    "place": "Baton Rouge ",
                    "publisher": "CRC Press LLC",
                },
                "keywords": [
                    {
                        "source": "EBL",
                        "value": "Magnetic materials -- Thermal properties.;"
                        "Adiabatic "
                        "demagnetization.;Refrigeration and refrigerating "
                        "machinery.",
                    }
                ],
                "languages": ["ENG"],
                "number_of_pages": "1",
                "publication_year": "2003",
                "subjects": [
                    {"scheme": "LOC", "value": "TK454.4.M3T57 2003"},
                    {"scheme": "DEWEY", "value": "538.4"},
                ],
                "table_of_content": [
                    "Front Cover",
                    "Contents",
                    "Preface",
                    "Acknowledgments",
                    "Chapter 1. Introduction",
                    "Chapter 2. Physics and models of magnetocaloric effect",
                    "Chapter 3. Methods of magnetocaloric properties " "investigation",
                    "Chapter 4. Magnetocaloric effect in 3d metals, alloys "
                    "and compounds",
                    "Chapter 5. Magnetocaloric effect in oxides",
                    "Chapter 6. Magnetocaloric effect in intermetallic " "compounds",
                    "Chapter 7. Magnetocaloric effect in rare "
                    "earth-metalloid compounds",
                    "Chapter 8. Magnetocaloric effect in rare earth metals "
                    "and alloys",
                    "Chapter 9. Magnetocaloric effect in amorphous materials",
                    "Chapter 10. Magnetocaloric effect in the systems with "
                    "superparamagnetic properties",
                    "Chapter 11. Application of the magnetocaloric effect "
                    "and magnetic materials in refrigeration apparatuses",
                    "Chapter 12. Conclusion",
                    "Appendix 1",
                    "Appendix 2",
                    "References",
                    "Index",
                    "Back Cover.",
                ],
                "title": "The Magnetocaloric Effect and Its Applications",
            },
        )
