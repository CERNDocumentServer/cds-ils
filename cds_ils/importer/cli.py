# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer command lines module."""

import click
from flask.cli import with_appcontext

from cds_ils.importer.api import import_from_xml
from cds_ils.importer.models import ImporterAgent, ImporterImportLog, ImporterMode
from cds_ils.importer.vocabularies_validator import validator as vocabulary_validator


@click.group()
def importer():
    """CDS-ILS importer commands."""
    # reset vocabularies validator cache
    vocabulary_validator.reset()


@importer.command()
@click.argument("sources", type=click.Path(exists=True, resolve_path=True), nargs=-1)
@click.option(
    "--provider",
    "-p",
    required=True,
    type=click.Choice(["springer", "cds", "ebl", "safari", "snv"]),
    help="Choose the provider",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    type=click.Choice(ImporterMode.get_options()),
    help="Choose the mode",
)
@with_appcontext
def import_from_file(sources, provider, mode, source_type="marcxml"):
    """Import from file command."""
    vocabulary_validator.reset()
    source = sources[0]

    log = ImporterImportLog.create(
        dict(
            agent=ImporterAgent.CLI,
            provider=provider,
            source_type=source_type,
            mode=mode,
            original_filename=source,
        )
    )
    import_from_xml(log, source, source_type, provider, mode, eager=True)
