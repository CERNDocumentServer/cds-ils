# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer exception handlers module."""

from cds_ils.importer.errors import ManualImportRequired, \
    MissingRequiredField, UnexpectedValue


def default_xml_exception_handler(exc, output, key, *args, **kwargs):
    """Default handler for xml to json conversion exceptions."""
    exc.message = exc.description = f"{exc.message} in <{key}{exc.subfield}> "
    raise exc


XMLImportHandlers = {
    UnexpectedValue: default_xml_exception_handler,
    MissingRequiredField: default_xml_exception_handler,
    ManualImportRequired: default_xml_exception_handler
}
