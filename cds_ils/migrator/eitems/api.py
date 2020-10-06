# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import io
import time
import uuid
from io import BytesIO

import click
import requests
from invenio_app_ils.documents.api import Document
from invenio_app_ils.documents.indexer import DocumentIndexer
from invenio_app_ils.eitems.api import EItem, EItemIdProvider
from invenio_app_ils.eitems.indexer import EItemIndexer
from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion

from cds_ils.migrator.documents.api import get_all_documents_with_files, \
    get_documents_with_ebl_eitems, get_documents_with_external_eitems, \
    get_documents_with_proxy_eitems
from cds_ils.migrator.errors import EItemMigrationError


def import_legacy_files(file_link):
    """Download file from legacy."""
    # needed to ignore the migrator in the legacy statistics
    download_request_headers = {"User-Agent": "CDS-ILS Migrator"}

    return io.BytesIO(
        requests.get(
            file_link, stream=True, headers=download_request_headers
        ).content
    )


def create_file(bucket, file_stream, filename):
    """Create file for given bucket."""
    file_record = ObjectVersion.create(bucket, filename, stream=file_stream)
    db.session.add(file_record)
    db.session.commit()
    return file_record


def create_eitem_with_bucket_for_document(document_pid):
    """Create EItem and its file bucket."""
    eitem = create_eitem(document_pid, open_access=True)
    with db.session.begin_nested():
        bucket = Bucket.create()
        eitem["bucket_id"] = str(bucket.id)
        eitem.commit()
    db.session.commit()
    return eitem, bucket


def create_eitem(document_pid, open_access=True):
    """Create eitem record."""
    obj = {"document_pid": document_pid, "open_access": open_access}
    record_uuid = uuid.uuid4()
    provider = EItemIdProvider.create(
        object_type="rec",
        object_uuid=record_uuid,
    )

    obj["pid"] = provider.pid.pid_value
    with db.session.begin_nested():
        eitem = EItem.create(obj, record_uuid)
        eitem.commit()
    db.session.commit()
    return eitem


def process_files_from_legacy():
    """Process legacy file."""
    results = get_all_documents_with_files()
    click.echo(
        "Found {} documents with files.".format(results.hits.total.value)
    )
    for hit in results:
        # try not to kill legacy server
        time.sleep(3)
        # make sure the document is in DB not only ES
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))
        for file_link in document["_migration"]["eitems_file_links"]:

            click.echo("File: {}".format(file_link))
            eitem, bucket = create_eitem_with_bucket_for_document(
                document["pid"]
            )

            # get filename
            file_name = file_link["description"]
            if not file_name:
                file_name = file_link.split("/")[-1]

            file_stream = import_legacy_files(file_link["value"])

            file = create_file(bucket, file_stream, file_name)
            click.echo("Indexing...")
            EItemIndexer().index(eitem)

        # make sure the files are not imported twice by setting the flag
        document["_migration"]["eitems_has_files"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)


def migrate_external_links():
    """Migrate external links from documents."""
    results = get_documents_with_external_eitems()
    click.echo(
        "Found {} documents with external links.".format(
            results.hits.total.value
        )
    )

    for hit in results:
        # make sure the document is in DB not only ES
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))

        for url in document["_migration"]["eitems_external"]:
            eitem = create_eitem(document["pid"], open_access=True)
            url["login_required"] = False
            eitem["urls"] = [url]
            eitem.commit()
            EItemIndexer().index(eitem)

        document["_migration"]["eitems_has_external"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)


def migrate_ezproxy_links():
    """Migrate external links from documents."""
    results = get_documents_with_proxy_eitems()
    click.echo(
        "Found {} documents with ezproxy links.".format(
            results.hits.total.value
        )
    )
    for hit in results:
        # make sure the document is in DB not only ES
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))

        for url in document["_migration"]["eitems_external"]:

            eitem = create_eitem(document["pid"], open_access=False)
            url["login_required"] = True
            eitem["urls"] = [url]
            eitem.commit()
            EItemIndexer().index(eitem)

        document["_migration"]["eitems_has_proxy"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)


def migrate_ebl_links():
    """Migrate external links from documents."""
    results = get_documents_with_ebl_eitems()
    click.echo(
        "Found {} documents with ebl links.".format(results.hits.total.value)
    )

    for hit in results:
        # make sure the document is in DB not only ES
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))

        # find the ebl identifier
        ebl_id = next(
            (
                x
                for x in document["alternative_identifiers"]
                if x["scheme"] == "EBL"
            ),
            None,
        )

        for url in document["_migration"]["eitems_ebl"]:

            if not ebl_id:
                raise EItemMigrationError(
                    "Document {pid} has no EBL alternative identifier"
                    " while EBL ebook link was found".format(
                        pid=document["pid"]
                    )
                )

            eitem = create_eitem(document["pid"], open_access=False)
            eitem["urls"] = [{"value": "EBL", "login_required": True}]
            eitem.commit()
            EItemIndexer().index(eitem)

        document["_migration"]["eitems_has_ebl"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)
