# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loan indexer APIs."""
from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PIDDeletedError


def index_extra_fields_for_loan(loan_dict):
    """Indexer hook to modify the loan record dict before indexing.

    The `item_suggestion` fields are added to the loan only on the search index
    because they are needed for search aggregation/filtering. They are not
    needed when fetching the loan details.
    """
    document_class = current_app_ils.document_record_cls
    item_suggestion = {}
    try:
        document_record = document_class.get_record_by_pid(loan_dict["document_pid"])
    except PIDDeletedError:
        # Document might have been deleted while reindexing asynchronously.
        return

    document = document_record.replace_refs()

    on_shelf = document["items"]["on_shelf"]

    is_request = (
        loan_dict["state"] in current_app.config["CIRCULATION_STATES_LOAN_REQUEST"]
    )

    # There may be no items on shelf, making impossible to suggest an item.
    if not on_shelf or not is_request:
        loan_dict["item_suggestion"] = item_suggestion
        return

    # Item_suggestion included due to a library request.
    # field was added to the loan indexer to avoid performing these operations
    # during CSV serialization - which would delay the process
    library = next(iter(on_shelf.values()))
    location = next(iter(library.values()))

    for item in location:
        item_not_on_loan = item.get("circulation") is None
        item_can_circulate = item["status"] == "CAN_CIRCULATE"
        if item_not_on_loan and item_can_circulate:
            item_suggestion = item

    for field in [
        "circulation_restriction",
        "internal_location_pid",
        "isbn",
        "pid",
    ]:
        item_suggestion.pop(field, None)

    loan_dict["item_suggestion"] = item_suggestion
