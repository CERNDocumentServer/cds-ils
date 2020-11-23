# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Admin panel for importer tasks."""
import json

from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_babelex import gettext as _
from markupsafe import Markup

from cds_ils.importer.models import ImporterTaskEntry, ImporterTaskLog


class ImporterTaskModelView(ModelView):
    """Invenio admin view for importer tasks."""

    # Entries are read-only
    can_create = False
    can_edit = False
    can_delete = False

    can_view_details = True

    column_display_pk = True

    column_default_sort = (ImporterTaskLog.id, True)


def _json_checkbox_formatter(view, context, model, name):
    """JSON handler for details page."""
    value = getattr(model, name)
    # value can be one of: None, [], {...}, [...]
    # first two are falsy, last two are truthy
    return bool(value)


def _json_code_formatter(view, context, model, name):
    """JSON handler for details page."""
    value = getattr(model, name)
    return Markup("<pre>{0}</pre>") \
        .format(json.dumps(value, indent=2, sort_keys=True)) if value \
        else None


class ImporterTaskEntryModelView(ModelView):
    """Invenio admin view for importer tasks."""

    # Entries are read-only
    can_create = False
    can_edit = False
    can_delete = False

    can_view_details = True

    column_display_pk = True

    column_default_sort = (
        ImporterTaskEntry.import_id, ImporterTaskEntry.entry_index
    )

    _json_object_columns = ["created_document", "created_eitem",
                            "updated_document", "updated_eitem", "series"]
    _json_array_columns = ["ambiguous_documents", "ambiguous_eitems",
                           "deleted_eitems", "fuzzy_documents"]
    _json_columns = [*_json_object_columns, *_json_array_columns]

    # display the id instead of __str__
    _common_formatters = {"importer_task": lambda v, c, m, n: m.import_id}

    column_formatters = {
        **_common_formatters,
        **{col: _json_checkbox_formatter for col in _json_columns},
    }

    column_formatters_detail = {
        **_common_formatters,
        **{col: _json_code_formatter for col in _json_columns},
    }


blueprint = Blueprint(
    "cds_ils_admin",
    __name__,
    template_folder="templates",
    static_folder="static",
)

importer_tasks = {
    "model": ImporterTaskLog,
    "modelview": ImporterTaskModelView,
    "name": "Tasks",
    "category": _("Importer"),
}

importer_records = {
    "model": ImporterTaskEntry,
    "modelview": ImporterTaskEntryModelView,
    "name": "Record updates",
    "category": _("Importer"),
}

__all__ = ("importer_tasks", "importer_records",)
