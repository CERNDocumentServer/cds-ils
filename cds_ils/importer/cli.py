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


@click.group()
def importer():
    """CDS-ILS importer commands."""


@importer.command()
@click.argument("sources", type=click.File("r"), nargs=-1)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["springer", "cds", "ebl", "safari"]),
    help="Choose the provider",
)
@with_appcontext
def import_from_file(sources, provider, source_type="marcxml"):
    """Import from file command."""
    import_from_xml(sources, source_type, provider)
