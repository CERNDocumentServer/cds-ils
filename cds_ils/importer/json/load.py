import uuid

import click
from dateutil import parser
from invenio_app_ils.documents.api import DocumentIdProvider
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils
from invenio_db import db

from cds_ils.importer.importer import Importer
from cds_ils.importer.models import ImporterMode
from cds_ils.importer.providers.cds.document_importer import CDSDocumentImporter
from cds_ils.importer.XMLRecordLoader import XMLRecordDumpLoader


class ILSLoader:

    def __init__(self, metadata_provider="cds"):
        self.metadata_provider = metadata_provider
        self.update_fields = None
        super().__init__()

    def load(self, entry):
        report = XMLRecordDumpLoader.import_from_json(
            entry, True, self.metadata_provider, ImporterMode.IMPORT.value
        )
        return report
