# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.
"""Tests for created relations betweeen records."""

from flask import current_app
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE, Document
from invenio_app_ils.series.api import SERIES_PID_TYPE, Series
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from cds_ils.migrator.relations.api import link_documents_and_serials
from cds_ils.minters import legacy_recid_minter
from tests.helpers import mint_record_pid


def test_journal_relation_from_publication_info(app):
    """Test journal-document relation from publication info field."""

    document_data = {
        "$schema": "https://127.0.0.1:5000/schemas/documents/document-v1.0.0.json",
        "created_by": {"type": "script", "value": "test"},
        "pid": "4321",
        "legacy_recid": "1111",
        "title": "Book: A Book",
        "document_type": "BOOK",
        "authors": [{"full_name": "Author Author"}],
        "abstracts": [{"value": "This is an abstract"}],
        "language": ["it"],
        "publication_year": "2020",
        "identifiers": [{"scheme": "ISBN", "value": "0123456789"}],
        "cover_metadata": {"ISBN": "0123456789"},
        "publication_info": [{"journal_issue": "issue"}],
        "_migration": {
            "has_journal": True,
            "journal_record_legacy_recids": [
                {
                    "recid": "1234",
                    "volume": None,
                }
            ],
        },
    }

    journal_data = {
        "$schema": "https://127.0.0.1:5000/schemas/series/series-v1.0.0.json",
        "pid": "serid-4",
        "title": "Dispersion Forces",
        "authors": ["Buhmann, Stefan Yoshi"],
        "abstract": "This is a multipart monograph",
        "mode_of_issuance": "SERIAL",
        "legacy_recid": "1234",
    }

    record_uuid = mint_record_pid(
        DOCUMENT_PID_TYPE, "pid", {"pid": document_data["pid"]}
    )
    document = Document.create(document_data, record_uuid)
    record_uuid = mint_record_pid(SERIES_PID_TYPE, "pid", {"pid": journal_data["pid"]})
    journal = Series.create(journal_data, record_uuid)
    legacy_pid_type = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]
    legacy_recid_minter(journal["legacy_recid"], legacy_pid_type, record_uuid)
    db.session.commit()
    ri = RecordIndexer()
    ri.index(document)
    ri.index(journal)
    current_search.flush_and_refresh(index="*")

    link_documents_and_serials()

    document_rec = Document.get_record_by_pid(document["pid"])
    assert "serial" in document_rec.relations
