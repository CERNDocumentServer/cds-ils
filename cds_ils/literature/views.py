# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Literature views."""

from flask import Blueprint, abort, current_app, redirect
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records.api import Record

from cds_ils.literature.api import get_record_by_legacy_recid

legacy_blueprint = Blueprint("cds_ils_legacy", __name__)


@legacy_blueprint.route("/legacy/<id>")
def legacy_redirect(id):
    """Redirect to the documents."""
    document_legacy_pid_type = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    series_legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
    is_document = False
    is_series = False

    # check if exists in ldocid
    try:
        record = get_record_by_legacy_recid(Record, document_legacy_pid_type, id)
        is_document = True
    except PIDDoesNotExistError:
        pass
    # check if exists in lserid
    try:
        record = get_record_by_legacy_recid(Record, series_legacy_pid_type, id)
        is_series = True
    except PIDDoesNotExistError:
        pass
    except PIDDeletedError as e:
        abort(410)

    if not is_document and not is_series:
        abort(404)

    documents_list_route = current_app.config["RECORDS_REST_ENDPOINTS"][
        DOCUMENT_PID_TYPE
    ]["list_route"]
    series_list_route = current_app.config["RECORDS_REST_ENDPOINTS"][SERIES_PID_TYPE][
        "list_route"
    ]

    url_path = series_list_route if is_series else documents_list_route

    return redirect("/api{0}{1}".format(url_path, record["pid"]))
