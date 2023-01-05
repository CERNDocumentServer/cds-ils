# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio App ILS Patrons views."""

from functools import wraps

from flask import Blueprint, abort, current_app
from invenio_app_ils.patrons.search import PatronsSearch
from invenio_app_ils.permissions import need_permissions
from invenio_circulation.search.api import search_by_patron_item_or_document
from invenio_rest import ContentNegotiatedMethodView

from .serializers import patron_loans_serializer


def pass_patron_from_es():
    """Decorator to retrieve a patron from ES."""

    def pass_patron_decorator(f):
        @wraps(f)
        def inner(self, person_id, *args, **kwargs):
            results = PatronsSearch().filter("term", person_id=person_id).execute()
            if not len(results.hits.hits):
                abort(404)
            patron = results.hits.hits[0]["_source"]
            return f(self, patron=patron.to_dict(), *args, **kwargs)

        return inner

    return pass_patron_decorator


def create_patron_loans_blueprint(app):
    """Create a blueprint for Patron's loans."""
    blueprint = Blueprint("cds_ils_patron_loans", __name__, url_prefix="")

    patron_loans = PatronLoansResource.as_view(PatronLoansResource.view_name, ctx={})
    url = "circulation/patrons/<int:person_id>/loans"
    blueprint.add_url_rule(url, view_func=patron_loans, methods=["GET"])

    return blueprint


class PatronLoansResource(ContentNegotiatedMethodView):
    """Patrons loans resource."""

    view_name = "patron_loans"

    def __init__(self, ctx, *args, **kwargs):
        """Constructor."""
        serializers = {"application/json": patron_loans_serializer}
        super().__init__(serializers, *args, **kwargs)

    @need_permissions("retrieve-patron-loans")
    @pass_patron_from_es()
    def get(self, patron, **kwargs):
        """Retrieve patron loans."""
        active_loan_states = current_app.config["CIRCULATION_STATES_LOAN_ACTIVE"]
        active_loans = search_by_patron_item_or_document(
            patron["id"], filter_states=active_loan_states
        )
        pending_loan_states = ["PENDING"]
        pending_loans = search_by_patron_item_or_document(
            patron["id"], filter_states=pending_loan_states
        )

        patron_loans = {
            "active_loans": active_loans,
            "pending_loans": pending_loans,
        }
        if patron.get("person_id"):
            patron_loans["person_id"] = patron["person_id"]
        if patron.get("department"):
            patron_loans["department"] = patron["department"]
        return self.make_response(patron_loans, code=200)
