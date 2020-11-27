# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Literature views."""

from flask import Blueprint, current_app, redirect
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record
from invenio_records_rest.errors import PIDDoesNotExistRESTError

from cds_ils.literature.api import get_record_by_legacy_recid

legacy_blueprint = Blueprint("cds_ils_legacy", __name__)


@legacy_blueprint.route("/legacy/<id>")
def legacy_redirect(id):
    """Redirect to the documents."""
    error = {
        "code": PIDDoesNotExistRESTError.code,
        "description": PIDDoesNotExistRESTError.description,
    }
    try:
        record = get_record_by_legacy_recid(Record, id)
    except PIDDoesNotExistError:
        return error
    schema = record["$schema"]
    Document = current_app_ils.document_record_cls
    is_document = schema.endswith(Document._schema)
    Series = current_app_ils.series_record_cls
    is_series = schema.endswith(Series._schema)
    if not is_document and not is_series:
        return error

    documents_list_route = current_app.config["RECORDS_REST_ENDPOINTS"][
        SERIES_PID_TYPE
    ]["list_route"]
    series_list_route = current_app.config["RECORDS_REST_ENDPOINTS"][
        DOCUMENT_PID_TYPE
    ]["list_route"]

    url_path = series_list_route if is_document else documents_list_route

    return redirect("/api{0}{1}".format(url_path, record["pid"]))
