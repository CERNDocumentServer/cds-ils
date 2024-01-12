# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Importer response serializers."""
import json

from flask import abort, current_app

from cds_ils.importer.models import ImporterImportLog


def importer_task_responsify(schema_class, mimetype):
    """Create an importer task serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    """

    def view(data, code=200, headers=None, record_offset=0):
        """Generate the response object."""
        if isinstance(data, ImporterImportLog):
            response_data = schema_class(record_offset=record_offset).dump(data)

            response = current_app.response_class(
                json.dumps(response_data), mimetype=mimetype
            )
            response.status_code = code

            if headers is not None:
                response.headers.extend(headers)
            return response
        else:
            abort(400)

    return view


def importer_task_log_responsify(schema_class, mimetype):
    """Create an importer tasks log serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    """

    def view(data, code=200, headers=None, **kwargs):
        """Generate the response object."""
        response_data = {}

        if isinstance(data, list):
            response_data = schema_class(many=True).dump(data)
        elif isinstance(data, ImporterImportLog):
            response_data = schema_class().dump(data)
        else:
            abort(400)

        response = current_app.response_class(
            json.dumps(response_data), mimetype=mimetype
        )
        response.status_code = code

        if headers is not None:
            response.headers.extend(headers)
        return response

    return view
