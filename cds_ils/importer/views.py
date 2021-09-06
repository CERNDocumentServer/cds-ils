# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Views for importer."""

import os

from flask import Blueprint, abort, current_app, request
from invenio_app_ils.permissions import need_permissions
from invenio_db import db
from invenio_rest import ContentNegotiatedMethodView
from sqlalchemy.orm.exc import ObjectDeletedError

from cds_ils.importer.api import allowed_files, rename_file
from cds_ils.importer.loaders.jsonschemas.schema import ImporterImportSchemaV1
from cds_ils.importer.models import ImporterTaskLog
from cds_ils.importer.serializers import task_entry_response, task_log_response
from cds_ils.importer.tasks import create_import_task


def create_importer_blueprint(app):
    """Add importer views to the blueprint."""
    blueprint = Blueprint("cds_ils_importer", __name__)

    list_view = ImporterListView.as_view(
        ImporterListView.view_name,
        default_media_type="application/json",
        serializers={
            'application/json': task_log_response,
        },
    )
    blueprint.add_url_rule(
        "/importer",
        view_func=list_view,
        methods=["POST", "GET"],
    )

    details_view = ImporterDetailsView.as_view(
        ImporterDetailsView.view_name,
        default_media_type="application/json",
        serializers={
            'application/json': task_entry_response,
        }
    )
    blueprint.add_url_rule(
        "/importer/<int:log_id>/offset/<int:offset>",
        view_func=details_view,
        methods=["GET"],
    )

    @blueprint.errorhandler(413)
    def payload_too_large(error):
        return {"message": "The file is too large", "status": 413}, 413

    return blueprint


class ImporterDetailsView(ContentNegotiatedMethodView):
    """Importer logs detail view."""

    view_name = "importer_details_view"

    def __init__(self, serializers=None, *args, **kwargs):
        """Constructor."""
        super(ImporterDetailsView, self).__init__(
            serializers,
            *args,
            **kwargs
        )

    @need_permissions("document-importer")
    def get(self, log_id, offset):
        """Returns the detail views of each subtask by given offset."""
        log = None
        try:
            log = db.session.query(ImporterTaskLog).get(log_id)
        except ObjectDeletedError:
            abort(404)
        if log:
            return self.make_response(log, record_offset=offset)
        else:
            abort(404, "Task not found")


class ImporterListView(ContentNegotiatedMethodView):
    """Importer logs list view."""

    view_name = "importer_list_view"

    def __init__(self, serializers=None, *args, **kwargs):
        """Constructor."""
        super(ImporterListView, self).__init__(
            serializers,
            *args,
            **kwargs
        )

    @need_permissions("document-importer")
    def post(self, **kwargs):
        """Import documents via a file."""
        if request.files:
            file = request.files["file"]
            form_data = ImporterImportSchemaV1().load(request.form)

            provider = form_data["provider"]
            mode = form_data["mode"]
            if not provider:
                abort(400, "Missing provider")

            if not mode:
                abort(400, "Missing mode")

            if allowed_files(file.filename):
                original_filename = file.filename
                file.filename = rename_file(file.filename)
                source_path = os.path.join(
                    current_app.config["CDS_ILS_IMPORTER_UPLOADS_PATH"],
                    file.filename
                )
                file.save(source_path)

                log = create_import_task(source_path,
                                         original_filename,
                                         provider, mode,
                                         )

                return self.make_response(log)
            else:
                abort(400, "That file extension is not allowed")
        else:
            abort(400, "Missing file")

    @need_permissions("document-importer")
    def get(self):
        """Get method."""
        list_count = 10
        logs = ImporterTaskLog.query \
            .order_by(ImporterTaskLog.id.desc()) \
            .limit(list_count).all()
        return self.make_response(logs)
