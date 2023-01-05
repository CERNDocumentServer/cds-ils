# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Tests for literature covers."""

from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.literature.covers import build_cover_urls, should_record_have_cover
from cds_ils.literature.tasks import pick_identifier_with_cover


def test_pick_identifier_with_cover_task(app, testdata, mocker):
    """Test update cover_metadata."""

    def _restore(original):
        """Restore the record to the original metadata."""
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(original["pid"])
        doc.clear()
        doc.update(original)
        doc.commit()
        db.session.commit()
        return doc

    def test_no_identifiers_no_previous_cover(doc):
        """It should not have cover_metadata because there are no ISBNs."""
        del doc["identifiers"]
        doc.pop("cover_metadata", "")  # delete if present
        doc.commit()
        db.session.commit()

        pick_identifier_with_cover(app, record=doc)
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(doc["pid"])
        assert "cover_metadata" not in doc

    def test_identifiers_deleted_with_previous_cover(doc):
        """It should remove the cover_metadata because there are no ISBNs."""
        del doc["identifiers"]
        doc["cover_metadata"] = dict(ISBN="112344343")
        doc.commit()
        db.session.commit()

        pick_identifier_with_cover(app, record=doc)
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(doc["pid"])
        assert "cover_metadata" not in doc

    def test_with_identifiers_with_valid_cover(doc):
        """It should have the ISBN in cover_metadata."""
        # return cover is valid
        mocker.patch("cds_ils.literature.tasks.is_valid_cover", return_value=True)

        doc["identifiers"] = [dict(scheme="ISBN", value="valid-isbn")]
        doc["cover_metadata"] = dict(ISBN="valid-isbn")
        doc.commit()
        db.session.commit()

        pick_identifier_with_cover(app, record=doc)
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(doc["pid"])
        assert doc["cover_metadata"] == dict(ISBN="valid-isbn")

    def test_with_invalid_identifiers_no_valid_cover(doc):
        """It should remove cover_metadata, the ISBN is not valid."""
        # return cover is not valid
        mocker.patch("cds_ils.literature.tasks.is_valid_cover", return_value=False)

        # the ISBN has been changed to a not valid one
        doc["identifiers"] = [dict(scheme="ISBN", value="not-valid-isbn")]
        # it had a previously valid ISBN
        doc["cover_metadata"] = dict(ISBN="valid-isbn")
        doc.commit()
        db.session.commit()

        pick_identifier_with_cover(app, record=doc)
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(doc["pid"])
        assert "cover_metadata" not in doc

    def test_add_new_identifier(doc):
        """It should change the cover_metadata to the new identifier."""
        # return cover is not valid
        mocker.patch("cds_ils.literature.tasks.is_valid_cover", return_value=True)

        # the ISBN has been changed to a not valid one
        doc["identifiers"] = [dict(scheme="ISBN", value="valid-isbn")]
        # it had a previously valid ISBN
        doc["cover_metadata"] = dict(ISBN="123456789")
        doc.commit()
        db.session.commit()

        pick_identifier_with_cover(app, record=doc)
        Document = current_app_ils.document_record_cls
        doc = Document.get_record_by_pid(doc["pid"])
        assert doc["cover_metadata"] == dict(ISBN="valid-isbn")

    dict_rec = testdata["documents"][0]
    Document = current_app_ils.document_record_cls
    doc = Document.get_record_by_pid(dict_rec["pid"])
    test_no_identifiers_no_previous_cover(doc)

    doc = _restore(dict_rec)
    test_identifiers_deleted_with_previous_cover(doc)

    doc = _restore(dict_rec)
    test_with_identifiers_with_valid_cover(doc)

    doc = _restore(dict_rec)
    test_with_invalid_identifiers_no_valid_cover(doc)

    doc = _restore(dict_rec)
    test_add_new_identifier(doc)


def test_cover_url_builder(app, testdata):
    """Test builder for cover urls."""
    doc = testdata["documents"][1]
    isbn = doc["cover_metadata"]["ISBN"]
    cover_urls = build_cover_urls(doc)
    assert cover_urls["small"].endswith("&ISBN={}/SC.gif".format(isbn))
    assert cover_urls["medium"].endswith("&ISBN={}/MC.gif".format(isbn))
    assert cover_urls["large"].endswith("&ISBN={}/LC.gif".format(isbn))

    series = testdata["series"][0]
    issn = series["cover_metadata"]["ISSN"]
    cover_urls = build_cover_urls(series)
    assert cover_urls["small"].endswith("&ISSN={}/SC.gif".format(issn))
    assert cover_urls["medium"].endswith("&ISSN={}/MC.gif".format(issn))
    assert cover_urls["large"].endswith("&ISSN={}/LC.gif".format(issn))

    doc_without_cover = testdata["documents"][0]
    cover_urls = build_cover_urls(doc_without_cover)
    assert cover_urls["small"].endswith("placeholder.png")
    assert cover_urls["medium"].endswith("placeholder.png")
    assert cover_urls["large"].endswith("placeholder.png")


def test_should_record_have_cover(app, testdata):
    """Test should_record_have_cover helper function."""
    doc = testdata["documents"][0]
    assert should_record_have_cover(doc)

    series = testdata["series"][0]
    assert should_record_have_cover(series)

    item = testdata["items"][0]
    assert not should_record_have_cover(item)
