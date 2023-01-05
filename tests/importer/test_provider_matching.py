from cds_dojson.matcher import matcher

from cds_ils.importer.providers.cds.models import document as cds_book
from cds_ils.importer.providers.ebl import ebl
from cds_ils.importer.providers.safari import safari
from cds_ils.importer.providers.springer import springer


def test_matcher():
    cds_document_blob1 = {"003": "SzGeCERN", "690C_": [{"a": "BOOK"}]}
    springer_document_blob1 = {"003": "DE-He213"}
    safari_document_blob1 = {"003": "OCoLC"}
    ebl_document_blob1 = {"003": "MiAaPQ"}
    assert cds_book.model == matcher(cds_document_blob1, "cds_ils.importer.models")
    assert springer.model == matcher(springer_document_blob1, "cds_ils.importer.models")
    assert safari.model == matcher(safari_document_blob1, "cds_ils.importer.models")
    assert ebl.model == matcher(ebl_document_blob1, "cds_ils.importer.models")
