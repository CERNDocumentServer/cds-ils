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

from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator
from cds_ils.migrator.acquisition.orders import import_orders_from_json
from cds_ils.migrator.api import (
    document_migration_report,
    import_documents_from_dump,
    items_migration_report,
)
from cds_ils.migrator.default_records import create_default_records, create_unknown_item
from cds_ils.migrator.document_requests.api import import_document_requests_from_json
from cds_ils.migrator.eitems.api import (
    migrate_ebl_links,
    migrate_external_links,
    migrate_ezproxy_links,
    migrate_safari_links,
    process_files_from_legacy,
)
from cds_ils.migrator.ill.api import import_ill_borrowing_requests_from_json
from cds_ils.migrator.internal_locations.api import import_internal_locations_from_json
from cds_ils.migrator.items.api import import_items_from_json
from cds_ils.migrator.loans.api import import_loans_from_json
from cds_ils.migrator.patrons.api import import_users_from_json
from cds_ils.migrator.providers.api import import_vendors_from_json
from cds_ils.migrator.relations.api import link_documents_and_serials
from cds_ils.migrator.relations.documents import migrate_document_siblings_relation
from cds_ils.migrator.relations.series import migrate_series_relations
from cds_ils.migrator.series.api import validate_serial_records
from cds_ils.migrator.series.series_import import (
    import_serial_from_file,
    import_series_from_dump,
)
from cds_ils.migrator.series.xml_multipart_loader import CDSMultipartDumpLoader
from cds_ils.migrator.utils import commit, reindex_pidtype


@click.group()
def migration():
    """CDS-ILS migrator commands."""
    records_formatter = logging.Formatter(
        "%(asctime)s, %(legacy_id)s, %(new_pid)s, %(status)s, %(message)s, "
    )

    eitems_formatter = logging.Formatter(
        "%(asctime)s, %(document_pid)s, %(new_pid)s, %(status)s, %(message)s, "
    )

    items_formatter = logging.Formatter(
        "%(asctime)s, %(legacy_id)s, %(new_pid)s, %(document_legacy_recid)s, %(status)s, %(message)s, "  # noqa
    )

    logged_record_types = {
        "serial": records_formatter,
        "multipart": records_formatter,
        "journal": records_formatter,
        "document": records_formatter,
        "item": items_formatter,
        "borrowing-request": records_formatter,
        "loan": records_formatter,
        "document-request": records_formatter,
        "acq-order": records_formatter,
        "eitem": eitems_formatter,
        "relation": records_formatter,
        "vocabularie": records_formatter,
    }

    for rectype, formatter in logged_record_types.items():
        record_logger_handler = FileHandler(f"/tmp/{rectype}s.log")
        record_logger_handler.setFormatter(formatter)
        record_logger = logging.getLogger(f"{rectype}s_logger")
        record_logger.addHandler(record_logger_handler)
        record_logger.setLevel("INFO")

    files_logger_handler = FileHandler(f"/tmp/file_list.log")
    files_logger = logging.getLogger(f"files_logger")
    files_logger.addHandler(files_logger_handler)

    # reset vocabularies validator cache
    vocabulary_validator.reset()


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
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def documents(sources, source_type, include, skip_indexing, fail_on_exceptions=False):
    """Migrate documents from CDS legacy."""
    import_documents_from_dump(
        sources=sources,
        source_type=source_type,
        eager=True,
        include=include,
        raise_exceptions=fail_on_exceptions,
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
        sources,
        rectype=rectype,
        loader_class=CDSMultipartDumpLoader,
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
@click.argument("sources", type=click.File("r"), nargs=-1)
@with_appcontext
def document_requests(sources):
    """Migrate document requests from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        import_document_requests_from_json(source)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def borrowing_requests(sources, fail_on_exceptions):
    """Migrate borrowing requests from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        import_ill_borrowing_requests_from_json(
            source, raise_exceptions=fail_on_exceptions
        )


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def acquisition_orders(sources, fail_on_exceptions):
    """Migrate acquisition orders and document requests from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating orders in {}...".format(idx, len(sources), source.name)
        )
        import_orders_from_json(source, raise_exceptions=fail_on_exceptions)


@migration.command()
@with_appcontext
def create_unknown_reference_records():
    """Create necessary records for required properties."""
    create_default_records()


@migration.command()
@with_appcontext
def create_default_item():
    """Create unknown item for migration of loans."""
    create_unknown_item()


@migration.command()
@click.argument("source", type=click.File("r"), nargs=-1)
@with_appcontext
def borrowers(source):
    """Migrate borrowers from CDS legacy."""
    import_users_from_json(source)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def loans(sources, fail_on_exceptions):
    """Migrate loans from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        import_loans_from_json(source, fail_on_exceptions)


@migration.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def loan_requests(sources, fail_on_exceptions):
    """Migrate loan_requests from CDS legacy."""
    for idx, source in enumerate(sources, 1):
        import_loans_from_json(source, fail_on_exceptions, mint_legacy_pid=False)


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
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def document_siblings(fail_on_exceptions):
    """Create sibling relations for migrated documents."""
    migrate_document_siblings_relation(raise_exceptions=fail_on_exceptions)


@relations.command()
@click.option(
    "--skip-indexing",
    is_flag=True,
)
@click.option(
    "--fail-on-exceptions",
    is_flag=True,
)
@with_appcontext
def series(skip_indexing, fail_on_exceptions):
    """Create relations for migrated series."""
    migrate_series_relations(raise_exceptions=fail_on_exceptions)
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


@migration.command()
@with_appcontext
def eitems_files():
    """Create eitems for migrated documents."""
    process_files_from_legacy()


@migration.command()
@with_appcontext
def eitems_providers():
    """Create eitems for migrated documents."""
    migrate_ezproxy_links()
    migrate_ebl_links()
    migrate_safari_links()
    migrate_external_links()


@migration.command()
@click.argument("log_file", type=click.File("r"), nargs=1)
@click.argument("recid_list_file", type=click.File("r"), nargs=1)
def documents_report(log_file, recid_list_file):
    """Provide documents migration summary."""
    document_migration_report(log_file, recid_list_file)


@migration.command()
@click.argument("log_file", type=click.File("r"), nargs=1)
@click.argument("recid_list_file", type=click.File("r"), nargs=1)
def items_report(log_file, recid_list_file):
    """Provide item migration summary."""
    items_migration_report(log_file, recid_list_file)
