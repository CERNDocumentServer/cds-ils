# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator CLI."""

import click
from flask.cli import with_appcontext

from cds_ils.migrator.api import commit, import_documents_from_dump, \
    import_documents_from_record_file, import_internal_locations_from_json, \
    import_items_from_json, import_parents_from_file, \
    link_and_create_multipart_volumes, link_documents_and_serials, \
    reindex_pidtype, validate_multipart_records, validate_serial_records


@click.group()
def migration():
    """CDS-ILS migrator commands."""


@migration.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@click.option(
    '--source-type',
    '-t',
    type=click.Choice(['json', 'marcxml', 'migrator-kit']),
    default='marcxml',
    help="Import from JSON, MARCXML or CDS-Migrator-Kit's _records.json file.")
@click.option(
    '--include',
    '-i',
    help='Comma-separated list of legacy recids to include in the import',
    default=None)
@with_appcontext
def documents(sources, source_type, include):
    """Migrate documents from CDS legacy."""
    with commit():
        if source_type == 'migrator-kit':
            import_documents_from_record_file(sources, include)
        else:
            import_documents_from_dump(
                sources=sources,
                source_type=source_type,
                eager=True,
                include=include
            )


@migration.command()
@click.argument('rectype', nargs=1, type=str)
@click.argument('source', nargs=1, type=click.File())
@click.option(
    '--include',
    '-i',
    help='Comma-separated list of legacy recids (for multiparts) or serial '
         'titles to include in the import',
    default=None)
@with_appcontext
def parents(rectype, source, include):
    """Migrate parents serials or multiparts from dumps."""
    click.echo('Migrating {}s...'.format(rectype))
    with commit():
        import_parents_from_file(source, rectype=rectype, include=include)


@migration.command()
@click.argument('source', type=click.File('r'), nargs=-1)
@click.option(
    '--include',
    '-i',
    help='Comma-separated list of legacy ids to include in the import',
    default=None)
@with_appcontext
def internal_locations(source, include):
    """Migrate documents from CDS legacy."""
    with commit():
        import_internal_locations_from_json(source, include=include)


@migration.command()
@click.argument('source', type=click.File('r'), nargs=-1)
@click.option(
    '--include',
    '-i',
    help='Comma-separated list of legacy recids to include in the import',
    default=None)
@with_appcontext
def items(source, include):
    """Migrate documents from CDS legacy."""
    with commit():
        import_items_from_json(source, include=include)


@migration.group()
def relations():
    """Migrate relations group."""


@relations.command()
@with_appcontext
def multipart():
    """Create relations for migrated multiparts."""
    with commit():
        link_and_create_multipart_volumes()
    reindex_pidtype('docid')
    reindex_pidtype('serid')


@relations.command()
@with_appcontext
def serial():
    """Create relations for migrated serials."""
    with commit():
        link_documents_and_serials()
    reindex_pidtype('docid')
    reindex_pidtype('serid')


@migration.group()
def validate():
    """Validate migrated record types."""


@validate.command(name='serial')
@with_appcontext
def validate_serial():
    """Validate migrated serials."""
    validate_serial_records()


@validate.command(name='multipart')
@with_appcontext
def validate_multipart():
    """Validate migrated multiparts."""
    validate_multipart_records()
