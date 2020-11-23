# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Views for importer."""

import json
import os
import uuid
from threading import Thread

import arrow
from flask import Blueprint, copy_current_request_context, flash, jsonify, \
    redirect, request, session
from invenio_app_ils.permissions import need_permissions
from werkzeug.utils import secure_filename

from cds_ils.importer.api import import_from_xml
from cds_ils.importer.models import ImporterAgent, ImporterMode, \
    ImporterTaskEntry, ImporterTaskLog


def create_importer_blueprint(app):
    """Add importer views to the blueprint."""
    blueprint = Blueprint("invenio_app_ils_importer", __name__)

    def allowed_files(filename):
        """Checks the extension of the files."""
        if "." not in filename:
            return False

        ext = filename.rsplit(".", 1)[1]
        if ext.upper() in app.config["IMPORTER_ALLOWED_EXTENSIONS"]:
            return True
        else:
            return False

    def rename_file(filename):
        """Renames filename with an unique name."""
        unique_filename = uuid.uuid4().hex
        ext = filename.rsplit(".", 1)[1]
        return unique_filename + "." + ext

    class RequestError(Exception):
        """Custom exception class to be thrown when error occurs."""

        def __init__(self, message, status, payload=None):
            self.message = message
            self.status = status
            self.payload = payload

    @blueprint.errorhandler(RequestError)
    def handle_request_error(error):
        """Catch RequestError exception, serialize into JSON, and respond."""
        payload = dict(error.payload or ())
        payload['status'] = error.status
        payload['message'] = error.message
        return jsonify(payload), error.status

    @blueprint.route('/importer/check/<log_id>', methods=['GET'])
    @need_permissions("document-importer")
    def check(log_id):
        log = ImporterTaskLog.query.filter_by(id=log_id).first()
        if log:
            entries = ImporterTaskEntry.query \
                .filter_by(import_id=log_id) \
                .order_by(ImporterTaskEntry.entry_index.asc()) \
                .all()
            obj = {
                "id": log_id,
                "state": log.status.value,  # enum value
                "start_time": arrow.get(log.start_time).isoformat(),
                "end_time": arrow.get(log.end_time).isoformat() \
                if log.end_time else None,
                "original_filename": log.original_filename,
                "provider": log.provider,  # string
                "mode": log.mode.value,  # enum value
                "source_type": log.source_type,  # string
            }
            if log.entries_count:
                obj["total_entries"] = log.entries_count
                obj["loaded_entries"] = len(entries)
            reports = []
            for entry in entries:
                if not entry.error:
                    reports.append({
                        "index": entry.entry_index,
                        "success": True,
                        "report": {
                            "ambiguous_documents": entry.ambiguous_documents,
                            "ambiguous_eitems": entry.ambiguous_eitems,
                            "created_document": entry.created_document,
                            "created_eitem": entry.created_eitem,
                            "updated_document": entry.updated_document,
                            "updated_eitem": entry.updated_eitem,
                            "deleted_eitems": entry.deleted_eitems,
                            "series": entry.series,
                            "fuzzy_documents": entry.fuzzy_documents,
                        }
                    })
                else:
                    reports.append({
                        "index": entry.entry_index,
                        "success": False,
                        "message": entry.error,
                    })
            obj["reports"] = reports
            return obj
        else:
            raise RequestError("Task not found", 404)

    @blueprint.route('/importer', methods=['POST'])
    @need_permissions("document-importer")
    def importer():

        @copy_current_request_context
        def import_from_xml_background(log_id, file, source_type, provider):
            """Acts as a proxy to pass the current context to the function."""
            import_from_xml(log_id, file, source_type, provider)

        def create_import_task(source_path, original_filename, source_type,
                               provider, mode):
            """Creates a task and returns its associated identifier."""
            importer_mode_map = dict(
                create=ImporterMode.CREATE,
                delete=ImporterMode.DELETE,
            )

            log = ImporterTaskLog.create(dict(
                agent=ImporterAgent.USER,
                provider=provider,
                source_type=source_type,
                mode=importer_mode_map[mode],
                original_filename=original_filename,
            ))

            t = Thread(target=import_from_xml_background,
                       args=(log.id, source_path, source_type, provider))
            t.start()

            return log.id

        if request.files:
            file = request.files["file"]
            provider = request.form.get("provider", None)
            mode = request.form.get("mode", None)

            if not provider:
                flash('Missing provider')
                raise RequestError('Missing provider', 400)

            if not mode:
                flash('Missing mode')
                raise RequestError('Missing mode', 400)

            if allowed_files(file.filename):
                original_filename = file.filename
                file.filename = rename_file(file.filename)
                if mode == 'delete':
                    session['name'] = "Test"
                    return redirect(request.url)
                filename = secure_filename(file.filename)
                source_path = os.path.join(app.config["IMPORTER_UPLOADS_PATH"],
                                           filename)
                file.save(source_path)

                source_type = "marcxml"
                log_id = create_import_task(source_path,
                                            original_filename,
                                            source_type,
                                            provider, mode)

                return (json.dumps({"id": log_id}),
                        200,
                        {'ContentType': 'application/json'})
            else:
                flash('That file extension is not allowed')
                raise RequestError('That file extension is not allowed', 400)
        else:
            raise RequestError('Missing file', 400)

    return blueprint
