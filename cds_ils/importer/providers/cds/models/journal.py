# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Journal model."""

from __future__ import unicode_literals

from copy import deepcopy

from cds_ils.importer.overdo import CdsIlsOverdo

from ..cds import get_helper_dict
from ..cds import model as cds_base
from ..ignore_fields import CDS_IGNORE_FIELDS
from .document import model as books_base


class CDSJournal(CdsIlsOverdo):
    """CDS Journal Overdo model."""

    __query__ = "980__:PERI -980__:DELETED -980__:MIGRATED"

    __model_ignore_keys__ = {
        "080__a",
        "020__C",
        "080__c",
        "030__a",
        "030__9",
        "044__a",
        "044__b",
        "222__a",
        "310__a",
        "340__a",
        "938__a",
        "044__a",
        "246_39",
        "85641m",
        "85641g",
        "85641n",
        "8564_8",  # not clear, some ID from legacy
        "8564_s",  # timestamp of files
        "8564_x",  # icon uri
        "6531_9",
        "246_3i",
        "650__a",
        "690C_a",
        "938__p",
        "938__f",
        "939__a",
        "939__d",
        "939__u",
        "939__v",
        "6531_a",
        "710__5",
        "770__t",  # title of relation has supplement
        "770__i",  # label of relation has supplement
        "772__i",  # label of relation supplement to
        "772__t",  # title of relation supplement to
        "780__i",  # label of relation continues
        "780__t",  # title of relation continues
        "785__i",  # label of relation continued by
        "785__t",  # title of relation continued by
        "787__i",  # label of relation language
        "787__t",  # title of relation language
        "85641y",
        "866__g",
        "866__x",
        "933__a",
        "962__n",
        "960__a",
        "960__c",
        "980__a",
        "980__b",
        "555__a",
        "85642x",
        "866__z",
        "938__i",
        "866__c",
        "85641a",
        "246_3C",
        "222__b",
        "340__z",
        "697C_a",
        "8564_z",
        "939__y",
        "2463_a",
        "595__a",
    }

    __ignore_keys__ = CDS_IGNORE_FIELDS | __model_ignore_keys__
    _default_fields = {"_migration": {**get_helper_dict(record_type="journal")}}

    rectype = "journal"

    def do(
        self,
        blob,
        ignore_missing=True,
        exception_handlers=None,
        init_fields=None,
    ):
        """Overwrite the do method."""
        init_fields = deepcopy(self._default_fields)
        return super().do(blob, ignore_missing, exception_handlers, init_fields)


model = CDSJournal(
    bases=(cds_base, books_base), entry_point_group="cds_ils.importer.series"
)
