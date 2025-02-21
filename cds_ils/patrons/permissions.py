# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS retrieve patron loans permissions."""

from invenio_access import action_factory
from invenio_access.permissions import Permission
from invenio_app_ils.permissions import (
    backoffice_access_action,
)
from invenio_app_ils.permissions import (
    views_permissions_factory as ils_views_permissions_factory,
)

retrieve_patron_loans_access_action = action_factory("retrieve-patron-loans-access")

document_importer_access_action = action_factory("document-importer-access")


def retrieve_patron_loans_permission(*args, **kwargs):
    """Return permission to retrieve patron loans."""
    return Permission(retrieve_patron_loans_access_action, backoffice_access_action)


def document_importer_permission(*args, **kwargs):
    """Return permission to access document importer."""
    return Permission(document_importer_access_action, backoffice_access_action)


def views_permissions_factory(action):
    """Override ILS views permissions factory."""
    if action == "retrieve-patron-loans":
        return retrieve_patron_loans_permission()
    elif action == "document-importer":
        return document_importer_permission()
    return ils_views_permissions_factory(action)
