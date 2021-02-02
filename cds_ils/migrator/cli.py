# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator CLI."""
import logging
from logging import FileHandler

import click
from flask.cli import with_appcontext

from cds_ils.migrator.acquisition.orders import import_orders_from_json
from cds_ils.migrator.acquisition.vendors import import_vendors_from_json
from cds_ils.migrator.api import import_documents_from_dump
from cds_ils.migrator.default_records import create_unknown_records
from cds_ils.migrator.document_requests.api import \
    import_document_requests_from_json
from cds_ils.migrator.eitems.api import migrate_ebl_links, \
    migrate_external_links, migrate_ezproxy_links, process_files_from_legacy
from cds_ils.migrator.ill.api import import_ill_borrowing_requests_from_json
from cds_ils.migrator.internal_locations.api import \
    import_internal_locations_from_json
from cds_ils.migrator.items.api import import_items_from_json
from cds_ils.migrator.loans.api import import_loans_from_json
from cds_ils.migrator.patrons.api import import_users_from_json
from cds_ils.migrator.relations.api import link_documents_and_serials, \
    migrate_document_siblings_relation, migrate_series_relations
from cds_ils.migrator.series.api import validate_multipart_records, \
    validate_serial_records
from cds_ils.migrator.series.series_import import import_serial_from_file, \
    import_series_from_dump
from cds_ils.migrator.series.xml_multipart_loader import CDSMultipartDumpLoader
from cds_ils.migrator.utils import commit, reindex_pidtype


@click.group()
def migration():
    """CDS-ILS migrator commands."""
    records_error_handler = FileHandler("/tmp/records_errored.log")
    migrated_records_handler = FileHandler("/tmp/records_migrated.log")

    records_logger = logging.getLogger("records_errored")
    migrated_records_logger = logging.getLogger("migrated_records")

    records_logger.addHandler(records_error_handler)
    migrated_records_logger.addHandler(migrated_records_handler)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--source-type",
    "-t",
    type=click.Choice(["json", "marcxml", "migrator-kit"]),
    default="marcxml",
    help="Import from JSON, MARCXML or CDS-Migrator-Kit's _records.json file.",
)
@click.option(
    "--include",
    "-i",
    help="Comma-separated list of legacy recids to include in the import",
    default=None,
)
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@with_appcontext
def documents(sources, source_type, include, skip_indexing):
    """Migrate documents from CDS legacy."""
    import_documents_from_dump(
        sources=sources,
        source_type=source_type,
        eager=True,
        include=include,
    )
    # We don't get the record back from _loadrecord so re-index all documents
    if not skip_indexing:
        reindex_pidtype("docid")


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@with_appcontext
def serial(sources, rectype="serial"):
    """Migrate serials from json file."""
    click.echo("Migrating {}s...".format(rectype))
    import_serial_from_file(sources, rectype=rectype)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@with_appcontext
def multipart(sources, rectype="multipart"):
    """Migrate multiparts from xml dump file."""
    click.echo("Migrating {}s...".format(rectype))
    import_series_from_dump(
        sources, rectype=rectype, loader_class=CDSMultipartDumpLoader
    )


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@with_appcontext
def journal(
    sources,
    skip_indexing,
    rectype="journal",
):
    """Migrate journals from xml dump file."""
    click.echo("Migrating {}s...".format(rectype))
    import_series_from_dump(sources, rectype=rectype)
    if not skip_indexing:
        reindex_pidtype("serid")


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@click.option(
    "--include",
    "-i",
    help="Comma-separated list of legacy ids to include in the import",
    default=None,
)
@with_appcontext
def internal_locations(source, include):
    """Migrate documents from CDS legacy."""
    with commit():
        import_internal_locations_from_json(source, include=include)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@with_appcontext
def items(sources, skip_indexing):
    """Migrate documents from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        import_items_from_json(source)
    if not skip_indexing:
        reindex_pidtype("pitmid")


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def vendors(source):
    """Migrate vendors from CDS legacy."""
    with commit():
        import_vendors_from_json(source)


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def document_requests(source):
    """Migrate document requests from CDS legacy."""
    with commit():
        import_document_requests_from_json(source)


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def borrowing_requests(source):
    """Migrate borrowing requests from CDS legacy."""
    with commit():
        import_ill_borrowing_requests_from_json(source)


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@click.option(
    "--include",
    "-i",
    help="Comma-separated list of legacy acquisition ids to include",
    default=None,
)
@with_appcontext
def acquisition_orders(source, include):
    """Migrate acquisition orders and document requests from CDS legacy."""
    with commit():
        import_orders_from_json(source, include=include)


@migration.command()
@with_appcontext
def create_unknown_reference_records():
    """Create necessary records for required properties."""
    create_unknown_records()


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def borrowers(source):
    """Migrate borrowers from CDS legacy."""
    import_users_from_json(source)


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def loans(source):
    """Migrate loans from CDS legacy."""
    import_loans_from_json(source)
    reindex_pidtype("loanid")


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def loan_requests(source):
    """Migrate loan_requests from CDS legacy."""
    import_loans_from_json(source)
    reindex_pidtype("loanid")


@migration.group()
def relations():
    """Migrate relations group."""


@relations.command()
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@with_appcontext
def serial(skip_indexing):
    """Create relations for migrated serials."""
    with commit():
        link_documents_and_serials()
    if not skip_indexing:
        reindex_pidtype("docid")
        reindex_pidtype("serid")


@relations.command()
@with_appcontext
def document_siblings():
    """Create sibling relations for migrated documents."""
    migrate_document_siblings_relation()


@relations.command()
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@with_appcontext
def series(skip_indexing):
    """Create relations for migrated series."""
    migrate_series_relations()
    if not skip_indexing:
        reindex_pidtype("serid")


@migration.group()
def validate():
    """Validate migrated record types."""


@validate.command(name="serial")
@with_appcontext
def validate_serial():
    """Validate migrated serials."""
    validate_serial_records()


@validate.command(name="multipart")
@with_appcontext
def validate_multipart():
    """Validate migrated multiparts."""
    validate_multipart_records()


@migration.command()
@with_appcontext
def eitems_files():
    """Create eitems for migrated documents."""
    process_files_from_legacy()


@migration.command()
@with_appcontext
def eitems_providers():
    """Create eitems for migrated documents."""
    migrate_external_links()
    migrate_ezproxy_links()
    migrate_ebl_links()
