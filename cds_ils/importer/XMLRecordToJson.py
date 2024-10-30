# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Importer Records loader."""

import datetime

from cds_dojson.marc21.utils import create_record
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from cds_ils.importer import marc21
from cds_ils.importer.errors import LossyConversion, UnrecognisedImportMediaType
from cds_ils.importer.handlers import xml_import_handlers


class XMLRecordToJson(object):
    """Handle record dump from marcxml."""

    def __init__(
        self,
        data,
        source_type="marcxml",
        latest_only=False,
        pid_fetchers=None,
        dojson_model=marc21,
        ignore_missing=False,
    ):
        """Initialize class."""
        self.resolver = Resolver(
            pid_type="recid", object_type="rec", getter=Record.get_record
        )
        self.data = data
        self.source_type = source_type
        self.latest_only = latest_only
        self.dojson_model = dojson_model
        self.revisions = None
        self.pid_fetchers = pid_fetchers or []
        self.ignore_missing = ignore_missing

    def dump(self):
        """Perform record dump."""
        dt = datetime.datetime.utcnow()

        marc_record = create_record(self.data)
        if "d" in marc_record.get("leader", []):
            is_deletable = True
        else:
            is_deletable = False

        init_fields = {}
        leader_tag = marc_record.get("leader", [])
        if "am" in leader_tag:
            init_fields.update({"_eitem": {"_type": "e-book"}})
        elif "im" in leader_tag or "jm" in leader_tag:
            init_fields.update({"_eitem": {"_type": "audiobook"}})
        elif "gm" in leader_tag:
            init_fields.update(
                {"document_type": "MULTIMEDIA", "_eitem": {"_type": "video"}}
            )
        else:
            raise UnrecognisedImportMediaType(leader_tag)
        # MARCXML -> JSON fields translation
        val = self.dojson_model.do(
            marc_record,
            exception_handlers=xml_import_handlers,
            init_fields=init_fields,
        )

        if not self.ignore_missing:
            # check for missing rules
            missing = self.dojson_model.missing(marc_record)

            if missing:
                raise LossyConversion(missing=missing)
        return dt, val, is_deletable
