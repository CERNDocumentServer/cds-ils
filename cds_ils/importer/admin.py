# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Admin panel for importer tasks."""
import json

from flask import Blueprint, url_for
from flask_admin.contrib.sqla import ModelView
from invenio_i18n import gettext as _
from markupsafe import Markup

from cds_ils.importer.models import ImporterImportLog, ImportRecordLog


def render_html_link(func):
    """Generate a object formatter for links."""

    def formatter(v, c, m, p):
        text, link = func(m)
        return Markup('<a href="{0}">{1}</a>'.format(link, text))

    return formatter


class ImporterTaskModelView(ModelView):
    """Invenio admin view for importer tasks."""

    # Entries are read-only
    can_create = False
    can_edit = False
    can_delete = False

    can_view_details = True

    column_display_pk = True

    column_default_sort = (ImporterImportLog.id, True)

    # Link to filter by import_id
    column_formatters = dict(
        records=render_html_link(
            lambda o: (
                "Record updates",
                url_for("importrecordlog.index_view", flt0_0=o.id),
            ),
        )
    )

    column_details_list = [
        *[c.key for c in ImporterImportLog.__table__.columns],
        "records",
    ]
    column_list = column_details_list

    column_filters = ("id",)


def _json_checkbox_formatter(view, context, model, name):
    """JSON handler for details page."""
    value = getattr(model, name)
    # value can be one of: None, [], {...}, [...]
    # first two are falsy, last two are truthy
    return bool(value)


def _json_code_formatter(view, context, model, name):
    """JSON handler for details page."""
    value = getattr(model, name)
    return (
        Markup("<pre>{0}</pre>").format(json.dumps(value, indent=2, sort_keys=True))
        if value
        else None
    )


class ImporterRecordLogModelView(ModelView):
    """Invenio admin view for importer tasks."""

    def is_visible(self):
        """Hide the view from the menu."""
        return False

    # Entries are read-only
    can_create = False
    can_edit = False
    can_delete = False

    can_view_details = True

    column_display_pk = True

    column_default_sort = (ImportRecordLog.id, ImportRecordLog.import_id)

    _json_object_columns = ["eitem", "document_json", "raw_json", "document"]
    _json_array_columns = ["partial_matches", "series"]
    _json_columns = [*_json_object_columns, *_json_array_columns]

    # display the id instead of __str__
    _common_formatters = {
        "importer_task": render_html_link(
            lambda o: (
                o.import_id,
                url_for("importerimportlog.index_view", flt0_0=o.import_id),
            ),
        )
    }

    column_formatters = {
        **_common_formatters,
        **{col: _json_checkbox_formatter for col in _json_columns},
    }

    column_formatters_detail = {
        **_common_formatters,
        **{col: _json_code_formatter for col in _json_columns},
    }

    column_filters = ("import_id",)


blueprint = Blueprint(
    "cds_ils_admin",
    __name__,
    template_folder="templates",
    static_folder="static",
)

importer_tasks = {
    "model": ImporterImportLog,
    "modelview": ImporterTaskModelView,
    "name": "Imports",
    "category": _("Importer"),
}

importer_records = {
    "model": ImportRecordLog,
    "modelview": ImporterRecordLogModelView,
    "name": "Record updates",
    "category": _("Importer"),
}

__all__ = (
    "importer_tasks",
    "importer_records",
)
