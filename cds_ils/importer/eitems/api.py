# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EItems Importer api."""
from invenio_app_ils.proxies import current_app_ils


def get_eitems_for_document_by_provider(document_pid, provider):
    """Find eitem by document pid and provider."""
    eitem_search = current_app_ils.eitem_search_cls()
    search = eitem_search.search_by_document_pid(document_pid=document_pid).filter(
        "term", created_by__value=provider
    )
    return search
