# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio App ILS Patron Loans Information views."""

from flask import jsonify
from invenio_app_ils.proxies import current_app_ils


def serialize_on_loan_literature_info(loan):
    """Serialize loan information."""
    Document = current_app_ils.document_record_cls
    document = Document.get_record_by_pid(loan["document_pid"])
    if "barcode" in loan["item"]:
        barcode = loan["item"]["barcode"]
    else:
        barcode = ""
    item = dict(
        pid=dict(type=loan["item_pid"]["type"], value=loan["item_pid"]["value"]),
        barcode=barcode,
    )
    return dict(
        item=item,
        start_date=loan["start_date"],
        end_date=loan["end_date"],
        title=document["title"],
    )


def serialize_loan_request_literature_info(loan):
    """Serialize loan information."""
    Document = current_app_ils.document_record_cls
    document = Document.get_record_by_pid(loan["document_pid"])
    return dict(
        request_start_date=loan["request_start_date"],
        request_end_date=loan["request_expire_date"],
        title=document["title"],
    )


def patron_loans_to_dict(patron_loans):
    """Serialize patron's loans information to dict.

    :param patron_loans: patron's loans
    :return: dict from patron's loan.
    :rtype: dict
    """
    literature_on_loan_results = patron_loans["active_loans"].scan()
    literature_on_loan = [
        serialize_on_loan_literature_info(loan) for loan in literature_on_loan_results
    ]

    loan_requests_results = patron_loans["pending_loans"].scan()
    loan_requests = [
        serialize_loan_request_literature_info(loan) for loan in loan_requests_results
    ]

    response = dict(
        on_loan=literature_on_loan,
        requests=loan_requests,
        person_id=patron_loans.get("person_id", ""),
        department=patron_loans.get("department", ""),
    )
    return response


def patron_loans_serializer(patron_loans, code=200, headers=None):
    """Serialize patron's loans."""
    response = jsonify(patron_loans_to_dict(patron_loans))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response
