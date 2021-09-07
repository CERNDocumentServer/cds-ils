from copy import deepcopy

from cds_ils.importer.documents.importer import DocumentImporter
from cds_ils.importer.providers.cds.utils import \
    add_title_from_conference_info, add_cds_url


class CDSDocumentImporter(DocumentImporter):
    """CDS Document importer class."""

    def _before_create(self):
        """Modify json before creating record."""
        add_title_from_conference_info(self.json_data)
        add_cds_url(self.json_data)
        return super()._before_create()
