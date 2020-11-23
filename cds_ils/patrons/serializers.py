# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio App ILS Patron Loans Information views."""

from flask import jsonify
from invenio_app_ils.locations.api import Location
from invenio_app_ils.proxies import current_app_ils


def serialize_on_loan_book_information(loan):
    """Serialize loan information."""
    location = Location.get_record_by_pid(loan["transaction_location_pid"])
    Document = current_app_ils.document_record_cls
    document = Document.get_record_by_pid(loan["document_pid"])
    return dict(
        barcode=loan["item"]["barcode"],
        end_date=loan["end_date"],
        library=location["name"],
        location=location["address"],
        title=document["title"],
    )


def serialize_loan_request_book_information(loan):
    """Serialize loan information."""
    location = Location.get_record_by_pid(loan["transaction_location_pid"])
    Document = current_app_ils.document_record_cls
    document = Document.get_record_by_pid(loan["document_pid"])
    return dict(
        request_start_date=loan["start_date"],
        request_end_date=loan["end_date"],
        library=location["name"],
        location=location["address"],
        title=document["title"],
    )


def patron_loans_to_dict(patron_loans):
    """Serialize patron's loans information to dict.

    :param patron_loans: patron's loans
    :return: dict from patron's loan.
    :rtype: dict
    """
    books_on_loan_results = patron_loans["active_loans"].hits.hits
    books_on_loan = [
        serialize_on_loan_book_information(loan["_source"])
        for loan in books_on_loan_results
    ]

    loan_requests_results = patron_loans["pending_loans"].hits.hits
    loan_requests = [
        serialize_loan_request_book_information(loan["_source"])
        for loan in loan_requests_results
    ]

    response = dict(
        books_on_loan=books_on_loan,
        loan_requests=loan_requests,
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
