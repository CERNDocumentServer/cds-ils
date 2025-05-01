# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS JSON Importer views module."""
from flask import abort, current_app, request
from invenio_app_ils.permissions import need_permissions
from invenio_app_ils.proxies import current_app_ils
from invenio_rest import ContentNegotiatedMethodView
from werkzeug.local import LocalProxy

from cds_ils.importer.json.importer import JSONImporter
from cds_ils.importer.loaders.jsonschemas.schema import ImporterRDMImportSchemaV1


def get_provider_by_content_type(content_type):
    """Selects import provider based on content type."""
    providers = LocalProxy(lambda: current_app.config["CDS_ILS_IMPORTER_PROVIDERS"])
    for provider, config in providers.items():
        if config.get("content_type") == content_type:
            return provider


class JSONImporterListView(ContentNegotiatedMethodView):
    """Importer logs detail view."""

    view_name = "json_importer_list_view"

    def __init__(self, serializers=None, *args, **kwargs):
        """Constructor."""
        super(JSONImporterListView, self).__init__(serializers, *args, **kwargs)

    @need_permissions("document-importer")
    def post(self, **kwargs):
        """Import documents via a file."""
        content_type = request.content_type

        form_data = ImporterRDMImportSchemaV1().load(request.json)
        provider = get_provider_by_content_type(content_type)
        mode = form_data.get("mode", None)
        json_data = form_data.get("data", None)

        if not provider:
            abort(400, "Content type does not match any provider.")

        report = JSONImporter(provider).run(json_data, mode)
        output_pid = report["output_pid"]
        document_class = current_app_ils.document_record_cls
        document = document_class.get_record_by_pid(output_pid)
        return self.make_response(record=document, pid=output_pid)
