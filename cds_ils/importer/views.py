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

import arrow
from flask import Blueprint, abort, request
from invenio_app_ils.permissions import need_permissions
from webargs import fields
from webargs.flaskparser import use_kwargs

from cds_ils.importer.models import ImporterAgent, ImporterMode, \
    ImporterTaskEntry, ImporterTaskLog
from cds_ils.importer.tasks import import_from_xml_task


def create_importer_blueprint(app):
    """Add importer views to the blueprint."""
    blueprint = Blueprint("invenio_app_ils_importer", __name__)

    def allowed_files(filename):
        """Checks the extension of the files."""
        allowed_extensions = app.config[
            "CDS_ILS_IMPORTER_FILE_EXTENSIONS_ALLOWED"
        ]
        return filename.lower().endswith(tuple(allowed_extensions))

    def rename_file(filename):
        """Renames filename with an unique name."""
        unique_filename = uuid.uuid4().hex
        ext = filename.rsplit(".", 1)[1]
        return unique_filename + "." + ext

    def dump_log(log):
        """Dumps a database log entry."""
        obj = {
            "id": log.id,
            "state": log.status.value,  # enum value
            "start_time": arrow.get(log.start_time).isoformat(),
            "end_time": (arrow.get(log.end_time).isoformat()
                         if log.end_time else None),
            "original_filename": log.original_filename,
            "provider": log.provider,  # string
            "mode": log.mode.value,  # enum value
            "source_type": log.source_type,  # string
        }
        if log.entries_count:
            obj["total_entries"] = log.entries_count
        return obj

    @blueprint.errorhandler(413)
    def payload_too_large(error):
        return {"message": "The file is too large", "status": 413}, 413

    @blueprint.route("/importer/check/<int:log_id>", methods=["GET"])
    @need_permissions("document-importer")
    def check(log_id):
        return check_next(log_id, 0)

    @blueprint.route("/importer/check/<int:log_id>/next/<int:next_entry>",
                     methods=["GET"])
    @need_permissions("document-importer")
    def check_next(log_id, next_entry):
        log = ImporterTaskLog.query.filter_by(id=log_id).first()
        if log:
            children_entries_query = ImporterTaskEntry.query \
                .filter_by(import_id=log_id)
            entries = children_entries_query \
                .filter(ImporterTaskEntry.entry_index >= next_entry) \
                .order_by(ImporterTaskEntry.entry_index.asc()) \
                .all()
            obj = dump_log(log)
            if log.entries_count:
                obj["loaded_entries"] = children_entries_query.count()
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
            abort(404, "Task not found")

    @blueprint.route("/importer", methods=["POST"])
    @use_kwargs({"provider": fields.Str(required=True)})
    @use_kwargs({"mode": fields.Str(required=True)})
    @need_permissions("document-importer")
    def importer(provider, mode):
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

            import_from_xml_task.apply_async((
                log.id, source_path, source_type, provider, mode,
            ))

            return log.id

        if request.files:
            file = request.files["file"]

            if not provider:
                abort(400, "Missing provider")

            if not mode:
                abort(400, "Missing mode")

            if allowed_files(file.filename):
                original_filename = file.filename
                file.filename = rename_file(file.filename)
                source_path = os.path.join(
                    app.config["CDS_ILS_IMPORTER_UPLOADS_PATH"],
                    file.filename
                )
                file.save(source_path)

                source_type = "marcxml"
                log_id = create_import_task(source_path,
                                            original_filename,
                                            source_type,
                                            provider, mode)

                return (json.dumps({"id": log_id}),
                        201,
                        {"ContentType": "application/json"})
            else:
                abort(400, "That file extension is not allowed")
        else:
            abort(400, "Missing file")

    @blueprint.route("/importer/list", methods=["GET"])
    @need_permissions("document-importer")
    def importer_list():
        list_count = 10
        logs = ImporterTaskLog.query \
            .order_by(ImporterTaskLog.id.desc()) \
            .limit(list_count).all()
        array = []
        for log in logs:
            array.append(dump_log(log))
        return {"results": array}

    return blueprint
