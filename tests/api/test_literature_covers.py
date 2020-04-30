# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Tests for literature covers."""

from mock import Mock

from cds_books.literature import tasks
from cds_books.literature.covers import build_syndetic_cover_urls, \
    is_record_with_cover, preemptively_set_first_isbn_as_cover
from cds_books.literature.tasks import pick_identifier_with_cover

tasks.is_valid_cover = Mock(return_value=True)
tasks.save_record = Mock(return_value=True)


def test_cover_url_builder(app, testdata):
    """Test builder for cover urls."""
    doc = testdata["documents"][0]
    isbn = doc["cover_metadata"]["ISBN"]
    cover_urls = build_syndetic_cover_urls(doc)
    assert cover_urls["small"].endswith("&ISBN={}/SC.gif".format(isbn))
    assert cover_urls["medium"].endswith("&ISBN={}/MC.gif".format(isbn))
    assert cover_urls["large"].endswith("&ISBN={}/LC.gif".format(isbn))

    serie = testdata["series"][0]
    issn = serie["cover_metadata"]["ISSN"]
    cover_urls = build_syndetic_cover_urls(serie)
    assert cover_urls["small"].endswith("&ISSN={}/SC.gif".format(issn))
    assert cover_urls["medium"].endswith("&ISSN={}/MC.gif".format(issn))
    assert cover_urls["large"].endswith("&ISSN={}/LC.gif".format(issn))

    doc_without_cover = testdata["documents"][1]
    cover_urls = build_syndetic_cover_urls(doc_without_cover)
    assert cover_urls["small"].endswith("placeholder.png")
    assert cover_urls["medium"].endswith("placeholder.png")
    assert cover_urls["large"].endswith("placeholder.png")


def test_is_record_with_cover(app, testdata):
    """Test is_record_with_cover helper function."""
    doc = testdata["documents"][0]
    assert is_record_with_cover(doc)

    series = testdata["series"][0]
    assert is_record_with_cover(series)

    item = testdata["items"][0]
    assert not is_record_with_cover(item)


def test_preemptively_set_first_isbn_as_cover(app, testdata):
    """Test to update cover_metadata value."""
    doc = testdata["documents"][1]
    preemptively_set_first_isbn_as_cover(app, record=doc)
    assert doc["cover_metadata"]["ISBN"] == "0123456789"

    serie = testdata["series"][1]
    preemptively_set_first_isbn_as_cover(app, record=serie)
    assert serie["cover_metadata"]["ISSN"] == "0123456789"


def test_pick_identifier_with_cover_task(app, testdata):
    """Test to update cover_metadata."""
    doc = testdata["documents"][1]
    pick_identifier_with_cover(app, record=doc)
    tasks.save_record.assert_called_once()

    series = testdata["series"][1]
    pick_identifier_with_cover(app, record=series)
    assert tasks.save_record.call_count == 2
