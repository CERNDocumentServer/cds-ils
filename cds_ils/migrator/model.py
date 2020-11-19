from cds_ils.importer.overdo import CdsIlsOverdo


class CdsIlsBase(CdsIlsOverdo):
    """Base model conversion MARC21 to JSON."""

model = CdsIlsBase(bases=(), entry_point_group='cds_ils.migrator.base')
