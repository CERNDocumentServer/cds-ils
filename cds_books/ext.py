# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature module."""


from invenio_records.signals import after_record_insert, after_record_update, \
    before_record_insert, before_record_update

from cds_books.literature.covers import preemptively_set_first_isbn_as_cover
from cds_books.literature.tasks import pick_identifier_with_cover


class CdsBooks(object):
    """CdsBooks extension."""

    def __init__(self, app=None):
        """Literature initialization."""
        self.register_signals(app)

    @staticmethod
    def register_signals(app):
        """Register Literature signals."""
        before_record_insert.connect(preemptively_set_first_isbn_as_cover)
        before_record_update.connect(preemptively_set_first_isbn_as_cover)
        after_record_insert.connect(pick_identifier_with_cover)
        after_record_update.connect(pick_identifier_with_cover)
