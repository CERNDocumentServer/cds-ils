# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, print_function

from cds_books.literature.covers import build_literature_cover_urls
from cds_books.literature.tasks import update_cover_metadata_isbn


def test_cover_url_builder(app, testdata):
    """Test builder for cover urls tasks."""
    doc = testdata["documents"][0]
    isbn = doc["cover_metadata"]["isbn"]

    cover_urls = build_literature_cover_urls(doc)
    assert cover_urls["small"].endswith("&isbn={}/SC.gif".format(isbn))
    assert cover_urls["medium"].endswith("&isbn={}/MC.gif".format(isbn))
    assert cover_urls["large"].endswith("&isbn={}/LC.gif".format(isbn))


def test_update_cover_metadata_isbn(app, testdata):
    """Test task to update cover_metadata."""
    doc_with_isbn = testdata["documents"][0]
    assert update_cover_metadata_isbn(doc_with_isbn) is None
