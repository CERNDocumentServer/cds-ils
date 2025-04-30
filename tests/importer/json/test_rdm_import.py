import json
import os

from cds_ils.importer.json.rdm.transform import RDMToILSTransform


def test_rdm_transformation(app):
    """Test springer record import translation."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "rdm_record.json"), "r") as fp:
        rdm_record = json.load(fp)
    output = RDMToILSTransform(rdm_record).transform()
    assert output == {
        "_eitem": {
            "urls": [
                {
                    "description": "e-book",
                    "value": "https://127.0.0.1/api/records/aey8d-bdw61/files/CERN-THESIS-2015-130.pdf",
                }
            ]
        },
        "_migration": {"eitems_external": None, "eitems_proxy": None},
        "_rdm_pid": "v2ha7-xyc73",
        "_serial": [
            {"title": "ALEPH Theses"},
            {
                "identifiers": [{"scheme": "ISSN", "value": "0356-0961"}],
                "title": "Series 0356-0961",
            },
        ],
        "abstract": "A new particle decaying to a pair of vector bosons was discovered in 2012 by the ATLAS and CMS experiments at the Large Hadron Collider. In the wake of this discovery a rush of measurements was made to characterize this particle. The four-lepton final state has been instrumental in both the discovery and characterization of this new particle. With only about 20 events seen in the resonance peak at 125GeV the CMS experiment has been able to make considerable progress in characterizing the Higgs-like boson using the wealth of information in this final state in concert with other decay modes. In addition to the search for this new boson we present three recent results in the study of the Higgs-like boson properties: studies of the production mode, total width, and spin-parity quantum numbers. First we present the search for this new resonance using the H to ZZ to 4l decay channel. Then we discuss the production mode measurement using this final state. Next, we present two results that provided breakthroughs in the study of the Higgs-like resonance. One is the measurement of the width from an interplay between the off-shell and on-shell production, setting a limit three orders of magnitude tighter than previous limits. The other is the tensor structure measurement of the bosons interactions with pairs of vector bosons, leading to constraints on its spin-parity properties, where only limited measurements had been done before. All of these results provide further confirmation that CMS has discovered a Higgs boson near 125GeV.",
        "alternative_abstracts": ["Some other abstract"],
        "alternative_titles": [
            {
                "language": "eng",
                "type": "TRANSLATED_TITLE",
                "value": "Construction of a central pre-sampler at "
                "ATLAS and study of ",
            },
            {
                "type": "ALTERNATIVE_TITLE",
                "value": "Construction of a central pre-sampler at "
                "{ATLAS} and study of ",
            },
        ],
        "alternative_identifiers": [
            {"scheme": "CDS", "value": "aey8d-bdw61"},
            {"scheme": "INSPIRE", "value": "1393422"},
        ],
        "agency_code": "SzGeCERN",
        "authors": [
            {
                "affiliations": [{"name": "Johns Hopkins U"}],
                "full_name": "Martin, Christopher Blake",
                "identifiers": [{"value": "0000-0003-1754-9027", "scheme": "ORCID"}],
                "type": "PERSON",
            }
        ],
        "conference_info": [
            {
                "acronym": "CHEP",
                "dates": "2025-01-01 - 2025-02-02",
                "identifiers": [{"scheme": "INSPIRE_CNUM", "value": "1234"}],
                "place": "Curacao",
                "title": "CHEP",
            }
        ],
        "copyrights": [{"statement": "2025 © Author(s)"}],
        "document_type": "BOOK",
        "edition": "2",
        "extensions": {
            "unit_accelerator": "CERN LHC",
            "unit_experiment": ["CMS"],
            "unit_project": [],
            "unit_study": [],
        },
        "identifiers": [
            {"scheme": "REPORT_NUMBER", "value": "CERN-THESIS-2015-130"},
            {"scheme": "REPORT_NUMBER", "value": "FERMILAB-THESIS-2015-22"},
            {"scheme": "REPORT_NUMBER", "value": "CMS-TS-2015-021"},
            {"scheme": "REPORT_NUMBER", "value": "CMS-TS-2015-021"},
        ],
        "imprint": {"date": "2015-04-22"},
        "internal_notes": [{"value": "NOTE NOTE"}],
        "keywords": [{"value": "HIGGS"}],
        "languages": ["eng"],
        "legacy_recid": "2050951",
        "licenses": [{"license": {"id": "CC-BY-4.0"}}],
        "number_of_pages": "245 p",
        # "other_authors": None,
        "publication_info": [
            {
                "artid": "10-12",
                "journal_issue": "2025/1",
                "journal_title": "Nature",
                "journal_volume": "1",
                "pages": "10-12",
            }
        ],
        "publication_year": "2015",
        "source": "CDS",
        # "subjects": None, # todo when UDC introduced in CDS_RDM
        "table_of_content": ["1. Chapter 1: ABC\n 2. Chapter 2: EFG"],
        "tags": ["THESIS"],
        "title": "Discovery and Characterization of a Higgs boson using four-lepton events from the CMS experiment",
        "urls": [{"value": "https://url.example.com/test"}],
        "restricted": False,
    }
