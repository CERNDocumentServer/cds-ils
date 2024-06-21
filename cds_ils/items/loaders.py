# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS items loaders."""

from invenio_app_ils.items.loaders.jsonschemas.items import (
    ItemSchemaV1 as ILSItemSchemaV1,
)
from invenio_app_ils.records.loaders import ils_marshmallow_loader
from invenio_app_ils.records.loaders.schemas.identifiers import IdentifierSchema
from marshmallow import ValidationError, fields


def validate_call_number_exists(identifiers):
    """Check if Call number exists."""
    for identifier in identifiers:
        if identifier["scheme"] == "CALL_NUMBER":
            return
    raise ValidationError("The Call number identifier field is mandatory.")


class ItemSchemaV1(ILSItemSchemaV1):
    """Item schema."""

    identifiers = fields.List(
        fields.Nested(IdentifierSchema),
        required=True,
        validate=validate_call_number_exists,
    )


item_loader = ils_marshmallow_loader(ItemSchemaV1)
