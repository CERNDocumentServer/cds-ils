# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Patron Indexer for CDS-ILS."""

from flask import current_app
from invenio_accounts.models import User
from invenio_app_ils.patrons.indexer import PatronBaseIndexer
from invenio_app_ils.patrons.indexer import PatronIndexer as ILSPatronIndexer
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount


class PatronIndexer(ILSPatronIndexer):
    """Indexer class for `Patron`."""

    def reindex_patrons(self):
        """Re-index all patrons."""
        # do not use PatronIndexer class otherwise it will trigger potentially
        # thousands of tasks to index referenced records
        indexer = PatronBaseIndexer()
        Patron = current_app_ils.patron_cls
        # cannot use bulk operation because Patron is not a real record
        index_local_accounts = current_app.config["CDS_ILS_INDEX_LOCAL_ACCOUNTS"]
        if index_local_accounts:
            all_user_ids = db.session.query(User.id).all()
        else:
            all_user_ids = db.session.query(RemoteAccount.user_id).all()
        for (user_id,) in all_user_ids:
            patron = Patron(user_id)
            indexer.index(patron)

        return len(all_user_ids)
