# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Importer loader."""
from flask import current_app
from marshmallow import Schema, fields, validate
from werkzeug.local import LocalProxy

from cds_ils.importer.models import ImporterMode

providers = LocalProxy(lambda: current_app.config["CDS_ILS_IMPORTER_PROVIDERS"])


class ImporterImportSchemaV1(Schema):
    """Schema for an importer task log."""

    provider = fields.String()
    mode = fields.String()
    ignore_missing_rules = fields.Boolean()


class ImporterRDMImportSchemaV1(Schema):
    """Schema for an importer task log."""

    data = fields.Dict(
        keys=fields.Str(), values=fields.Raw(), allow_none=False, load_default=dict
    )
    mode = fields.String(
        required=True, validate=validate.OneOf(choices=ImporterMode.get_options())
    )
