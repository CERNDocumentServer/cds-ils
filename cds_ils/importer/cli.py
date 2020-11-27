# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer command lines module."""
import click
from flask.cli import with_appcontext
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

from cds_ils.importer.api import import_record, records_logger
from cds_ils.importer.errors import LossyConversion, \
    ProviderNotAllowedDeletion, RecordNotDeletable
from cds_ils.importer.models import ImporterAgent, ImporterMode, \
    ImporterTaskEntry, ImporterTaskLog
from cds_ils.importer.parse_xml import get_records_list


@click.group()
def importer():
    """CDS-ILS importer commands."""


@importer.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--provider",
    "-p",
    required=True,
    type=click.Choice(["springer", "cds", "ebl", "safari"]),
    help="Choose the provider",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    type=click.Choice(["create", "delete"]),
    help="Choose the mode",
)
@with_appcontext
def import_from_file(sources, provider, mode, source_type="marcxml"):
    """Import from file command."""
    import_from_xml(sources, provider, mode, source_type)


def import_from_xml(sources, provider, mode, source_type, eager=True):
    """Load xml files."""
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Importing documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        log = ImporterTaskLog.create(dict(
            agent=ImporterAgent.CLI,
            provider=provider,
            source_type=source_type,
            mode=ImporterMode.CREATE,  # commands act as create
            original_filename=source.name,
        ))

        entry_data = None
        try:
            records_list = list(get_records_list(source))
            log.entries_count = len(records_list)
            db.session.commit()
            for i, record in enumerate(records_list):
                entry_data = dict(
                    import_id=log.id,
                    entry_index=i,
                )
                click.secho("Processing record {}".format(i))

                try:
                    report = import_record(
                        record, provider, mode,
                        source_type=source_type, eager=True
                    )
                except (LossyConversion, RecordNotDeletable,
                        ProviderNotAllowedDeletion) as e:
                    click.secho("Failed to import entry", fg="red")
                    ImporterTaskEntry.create_failure(entry_data, e)
                    continue

                click.secho(
                    "Created: {}\n "
                    "Updated: "
                    "{}\n "
                    "Ambiguous matches {}\n "
                    "Fuzzy matches {}\n".format(
                        report["created"],
                        report["updated"],
                        report["ambiguous_documents"],
                        report["fuzzy"],
                    ),
                    fg="blue",
                )
                ImporterTaskEntry.create_success(entry_data, report)

        except IlsValidationError as e:
            records_logger.error(
                "@FILE: {0} FATAL: {1}".format(
                    source.name,
                    str(e.original_exception.message),
                )
            )
            if entry_data:
                ImporterTaskEntry.create_failure(entry_data, e)
            log.set_failed(e)
            continue

        except Exception as e:
            records_logger.error(
                "@FILE: {0} ERROR: {1}".format(source.name, str(e))
            )
            if entry_data:
                ImporterTaskEntry.create_failure(entry_data, e)
            log.set_failed(e)
            raise e

        log.set_succeeded()
