# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from flask import current_app
from invenio_app_ils.proxies import current_app_ils


def test_local_accounts_indexing(app, patrons, testdata):
    """Test if local accounts get indexed or not."""

    current_app_ils.patron_indexer.reindex_patrons()

    index_local_accounts = current_app.config["CDS_ILS_INDEX_LOCAL_ACCOUNTS"]
    if not index_local_accounts:
        assert current_app_ils.patron_indexer.reindex_patrons() == 1
    else:
        assert current_app_ils.patron_indexer.reindex_patrons() == 2
