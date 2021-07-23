# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Importer loader."""
from marshmallow import Schema, fields


class ImporterImportSchemaV1(Schema):
    """Schema for an importer task log."""

    provider = fields.String()
    mode = fields.String()
    ignore_missing_rules = fields.Boolean()
