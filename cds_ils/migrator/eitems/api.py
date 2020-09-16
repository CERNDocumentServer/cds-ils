import io
import uuid
from io import BytesIO

import click
import requests
from invenio_app_ils.documents.api import Document
from invenio_app_ils.documents.indexer import DocumentIndexer
from invenio_app_ils.eitems.api import EItemIdProvider, EItem
from invenio_app_ils.eitems.indexer import EItemIndexer
from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion

from cds_ils.migrator.documents.api import get_all_documents_with_files


def import_legacy_files(file_link):
    """Download file from legacy."""

    return io.BytesIO(requests.get(file_link, stream=True).content)


def create_file(bucket, file_stream, filename):
    """Create file for given bucket."""

    file_record = ObjectVersion.create(bucket, filename, stream=file_stream)
    db.session.add(file_record)
    db.session.commit()
    return file_record


def create_eitem_with_bucket_for_document(document_pid):
    """Create EItem record."""

    obj = {"document_pid": document_pid, "open_access": True}
    record_uuid = uuid.uuid4()
    provider = EItemIdProvider.create(
        object_type="rec",
        object_uuid=record_uuid,
    )

    obj["pid"] = provider.pid.pid_value
    with db.session.begin_nested():
        eitem = EItem.create(obj, record_uuid)
        eitem.commit()
        bucket = Bucket.create()
        eitem["bucket_id"] = str(bucket.id)
        eitem.commit()
    db.session.commit()
    return eitem, bucket


def process_files_from_legacy():
    documents_with_files = get_all_documents_with_files()
    click.echo("Found {} documents with files.".format(
        documents_with_files.hits.total.value))
    for hit in documents_with_files:

        # make sure the document is in DB not only ES
        document = Document.get_record_by_pid(hit.pid)
        click.echo("Processing document {}...".format(document['pid']))
        for file_link in document["_migration"]["eitems_file_links"]:

            click.echo("File: {}".format(file_link))
            eitem, bucket = create_eitem_with_bucket_for_document(
                document["pid"])

            # get filename
            file_name = file_link['description']
            if not file_name:
                file_name = file_link.split('/')[-1]

            file_stream = import_legacy_files(file_link['url'])

            file = create_file(bucket, file_stream, file_name)
            click.echo("Indexing...")
            EItemIndexer().index(eitem)

        # make sure the files are not imported twice by setting the flag
        document['_migration']['eitems_has_files'] = False
        document.commit()
        db.session.commit()
        DocumentIndexer().index(document)


def process_file_from_dump():
    pass
