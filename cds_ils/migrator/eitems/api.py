# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""
import hashlib
import io
import logging
import time
import uuid

import click
import requests
from invenio_app_ils.documents.indexer import DocumentIndexer
from invenio_app_ils.eitems.api import EItem, EItemIdProvider
from invenio_app_ils.eitems.indexer import EItemIndexer
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion

from cds_ils.migrator.documents.api import get_all_documents_with_files, \
    get_documents_with_ebl_eitems, get_documents_with_external_eitems, \
    get_documents_with_proxy_eitems
from cds_ils.migrator.errors import EItemMigrationError, FileMigrationError

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_legacy_files(file_link):
    """Download file from legacy."""
    # needed to ignore the migrator in the legacy statistics
    download_request_headers = {"User-Agent": "CDS-ILS Migrator"}

    file_response = requests.get(
        file_link, stream=True, headers=download_request_headers
    )

    file_content_stream = io.BytesIO(file_response.content)

    return file_content_stream


def create_file(bucket, file_stream, filename, dump_file_checksum):
    """Create file for given bucket."""
    file_record = ObjectVersion.create(bucket, filename, stream=file_stream)
    assert file_record.file.checksum == "md5:{}".format(dump_file_checksum)

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
    obj = {"document_pid": document_pid,
           "open_access": open_access,
           "created_by": {"type": "script", "value": "migration"}
           }
    record_uuid = uuid.uuid4()
    provider = EItemIdProvider.create(
        object_type="rec",
        object_uuid=record_uuid,
    )

    obj["pid"] = provider.pid.pid_value
    eitem = EItem.create(obj, record_uuid)
    return eitem


def process_files_from_legacy():
    r"""Process legacy file.

    File dump object
    {
      "comment": null,
      "status": "",
      "version": 1,
      "encoding": null,
      "creation_date": "2014-08-15T16:27:10+00:00",
      "bibdocid": 952822,
      "mime": "application/pdf",
      "full_name": "075030183X_TOC.pdf",
      "superformat": ".pdf",
      "recids_doctype": [
        [
          262151,
          "Additional",
          "075030183X_TOC.pdf"
        ]
      ],
      "path": "/opt/cdsweb/var/data/files/g95/952822/content.pdf;1",
      "size": 264367,
      "license": {},
      "modification_date": "2014-08-15T16:27:10+00:00",
      "copyright": {},
      "url": "http://cds.cern.ch/record/262151/files/075030183X_TOC.pdf",
      "checksum": "a8b4bba8a2bbc6780cc7707387c4702f",
      "description": "1. Table of contents",
      "format": ".pdf",
      "name": "075030183X_TOC",
      "subformat": "",
      "etag": "\"952822.pdf1\"",
      "recid": 262151,
      "flags": [],
      "hidden": false,
      "type": "Additional",
      "full_path": "/opt/cdsweb/var/data/files/g95/952822/content.pdf;1"
    }
    """
    search = get_all_documents_with_files()

    click.echo("Found {} documents with files.".format(search.count()))
    for hit in search.scan():
        # try not to kill legacy server
        time.sleep(3)
        # make sure the document is in DB not only ES
        Document = current_app_ils.document_record_cls
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))

        try:
            for file_dump in document["_migration"]["files"]:

                # check if url migrated from MARC
                url_in_marc = [
                    item
                    for item in document["_migration"]["eitems_file_links"]
                    if item["value"] == file_dump["url"]
                ]
                if not url_in_marc:
                    msg = (
                        "DOCUMENT: {pid}: ERROR: File {file}"
                        " found in the dump but not in MARC".format(
                            pid=document.pid, file=file_dump["url"]
                        )
                    )
                    raise FileMigrationError(msg)

                click.echo("File: {}".format(file_dump["url"]))
                eitem, bucket = create_eitem_with_bucket_for_document(
                    document["pid"]
                )

                # get filename
                file_name = file_dump["description"]
                if not file_name:
                    file_name = file_dump["full_name"]

                file_stream = import_legacy_files(file_dump["url"])

                file = create_file(
                    bucket, file_stream, file_name, file_dump["checksum"]
                )
                click.echo("Indexing...")
                EItemIndexer().index(eitem)
        except Exception as e:
            msg = "DOCUMENT: {pid} CAN'T MIGRATE FILES ERROR: {error}".format(
                pid=document["pid"], error=str(e)
            )
            click.secho(msg)
            records_logger.error(msg)
            continue

        # make sure the files are not imported twice by setting the flag
        document["_migration"]["eitems_has_files"] = False
        document["_migration"]["has_files"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)


def migrate_external_links():
    """Migrate external links from documents."""
    search = get_documents_with_external_eitems()
    click.echo(
        "Found {} documents with external links.".format(search.count())
    )

    for hit in search.scan():
        # make sure the document is in DB not only ES
        Document = current_app_ils.document_record_cls
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
    search = get_documents_with_proxy_eitems()
    click.echo("Found {} documents with ezproxy links.".format(search.count()))
    for hit in search.scan():
        # make sure the document is in DB not only ES
        Document = current_app_ils.document_record_cls
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
    search = get_documents_with_ebl_eitems()
    click.echo("Found {} documents with ebl links.".format(search.count()))

    url_template = \
        "http://ebookcentral.proquest.com/lib/cern/detail.action?docID={}"

    for hit in search.scan():
        # make sure the document is in DB not only ES
        Document = current_app_ils.document_record_cls
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document["pid"]))

        # find the ebl identifier
        ebl_id_list = [x for x in document["alternative_identifiers"] if
                       x["scheme"] == "EBL"]

        if not ebl_id_list:
            raise EItemMigrationError(
                "Document {pid} has no EBL alternative identifier"
                " while EBL ebook link was found".format(
                    pid=document["pid"]
                )
            )

        for url in document["_migration"]["eitems_ebl"]:
            matched_ebl_id = [ebl_id["value"] for ebl_id in
                              ebl_id_list if ebl_id["value"] in url["value"]]

            if not matched_ebl_id:
                raise EItemMigrationError(
                    "Document {pid} has different EBL identifier"
                    " than the ID specified in the url parameters".format(
                        pid=document["pid"]
                    )
                )
            eitem = create_eitem(document["pid"], open_access=False)
            eitem["urls"] = [
                {
                    "value": url_template.format(matched_ebl_id[0]),
                    "login_required": True
                }
            ]
            eitem.commit()
            EItemIndexer().index(eitem)

        document["_migration"]["eitems_has_ebl"] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)
