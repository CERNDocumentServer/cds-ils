from cds_dojson.matcher import matcher

from cds_ils.importer.providers.cds import cds
from cds_ils.importer.providers.springer import springer


def test_matcher():
    cds_document_blob1 = {"003": "SzGeCERN"}
    springer_document_blob1 = {"003": "DE-He213"}
    assert cds.model == matcher(cds_document_blob1, "cds_ils.marc21.models")
    assert springer.model == matcher(
        springer_document_blob1, "cds_ils.marc21.models"
    )
