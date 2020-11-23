#  -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Literature views."""

from flask import Blueprint, redirect
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_rest.errors import PIDDoesNotExistRESTError

legacy_blueprint = Blueprint("cds_ils_legacy", __name__)


@legacy_blueprint.route("/legacy/<id>")
def legacy_redirect(id):
    """Redirect to the documents."""
    try:
        Document = current_app_ils.document_record_cls
        record = Document.get_record_by_legacy_recid(id)
    except PIDDoesNotExistError:
        return {
            "code": PIDDoesNotExistRESTError.code,
            "description": PIDDoesNotExistRESTError.description,
        }

    return redirect("/api/documents/{0}".format(record.get("pid")))
