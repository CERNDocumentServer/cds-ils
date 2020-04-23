# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature module."""


from invenio_records.signals import after_record_insert, after_record_update, \
    before_record_insert, before_record_update

from .tasks import set_cover, update_cover


class CdsBooksLiterature(object):
    """CdsBooksLiterature extension."""

    def __init__(self, app=None):
        """Literature initialization."""
        self.register_signals(app)

    @staticmethod
    def register_signals(app):
        """Register Literature signals."""
        before_record_insert.connect(update_cover)
        before_record_update.connect(update_cover)
        after_record_insert.connect(set_cover)
        after_record_update.connect(set_cover)
