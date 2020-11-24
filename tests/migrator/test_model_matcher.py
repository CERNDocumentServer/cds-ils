import pytest
from cds_dojson.matcher import matcher
from dojson.contrib import marc21 as default

from cds_ils.importer.providers.cds.models import book, journal, multipart, \
    serial, standard


def test_marc21_matcher_books():
    """Test CDS DoJSON matcher - books."""
    book_blob1 = {"003": "SzGeCERN", "690C_": [{"a": "BOOK"}]}
    book_blob2 = {"003": "SzGeCERN", "980__": [{"a": "PROCEEDINGS"}]}
    book_blob3 = {"003": "SzGeCERN", "697C_": [{"a": "ENGLISH BOOK CLUB"}]}
    serial_blob1 = {
        "003": "SzGeCERN",
        "690C_": [{"a": "BOOK"}],
        "490__": {"a": "Test title"},
    }
    cds_blob2 = {
        "003": "SzGeCERN",
    }
    multipart_blob1 = {
        "003": "SzGeCERN",
        "690C_": [{"a": "BOOK"}],
        "245__": [{"a": "Test "}],
        "596__": [{"a": "MULTIVOLUMES"}],
        "246__": [{"p": "Volume Title", "n": "2"}],
    }
    multipart_blob2 = {
        "003": "SzGeCERN",
        "690C_": [{"a": "BOOK"}],
        "245__": [{"a": "Test "}],
        "246__": [{"n": "2"}],
        "596__": [{"a": "MULTIVOLUMES"}],
    }
    standard_blob1 = {"003": "SzGeCERN", "690C_": [{"a": "STANDARD"}]}
    journal_blob = {"003": "SzGeCERN", "980__": [{"a": "PERI"}]}
    not_match = {"foo": "bar"}

    models_entrypoint = "cds_ils.importer.models"
    series_models_entrypoint = "cds_ils.importer.series_models"
    assert book.model == matcher(book_blob1, models_entrypoint)
    assert book.model == matcher(book_blob2, models_entrypoint)

    with pytest.raises(AssertionError):
        # English book club should not be matched
        assert book.model == matcher(book_blob3, models_entrypoint)
    assert standard.model == matcher(standard_blob1, models_entrypoint)
    assert serial.model == matcher(serial_blob1, series_models_entrypoint)
    assert multipart.model == matcher(
        multipart_blob1, series_models_entrypoint
    )
    assert multipart.model == matcher(
        multipart_blob2, series_models_entrypoint
    )
    assert journal.model == matcher(journal_blob, series_models_entrypoint)
    # make sure that it won't match with any CDS record
    assert default.model == matcher(cds_blob2, models_entrypoint)
    assert default.model == matcher(not_match, models_entrypoint)
