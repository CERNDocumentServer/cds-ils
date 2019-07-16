from __future__ import absolute_import, print_function

import json
import os
import re

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_app_ils.records.api import Series, Keyword
from invenio_db import db
from invenio_migrator.cli import _loadrecord, dumps
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record

from cds_books.migrator.records import CDSParentRecordDumpLoader


def load_dumps_from_dir(source_dir, rectype):
    with click.progressbar(os.listdir(source_dir)) as bar:
        for filename in bar:
            click.echo('Loading dump {0}'.format(filename))
            if re.match(r'^'+rectype+'_(\d+)(_\d+)*.json$', filename):
                with open(source_dir+filename, 'r') as file:
                    json_dump = json.load(file)
                    import_parent_records(rectype, json_dump)


def import_parent_records(rectype, dump):
    try:
        CDSParentRecordDumpLoader.create(
            dump, model=identify_model(rectype))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def identify_model(rectype):
    if rectype == 'serial' or rectype == 'multipart':
        return Series
    elif rectype == 'keywords':
        return Keyword
    else:
        return Record


def load_records(sources, source_type, eager, rectype):
    """Load records."""
    for idx, source in enumerate(sources, 1):
        click.echo('Loading dump {0} of {1} ({2})'.format(
            idx, len(sources), source.name))
        data = json.load(source)
        with click.progressbar(data) as records:
            for item in records:
                count = PersistentIdentifier.query.filter_by(
                            pid_type='serid', pid_value=str(item['recid'])).count()
                if count > 0:
                    current_app.logger.warning(
                        "migration: duplicate {0}".format(item['recid']))
                else:
                    try:
                        _loadrecord(item, source_type, eager=eager)
                    except PIDAlreadyExists:
                        current_app.logger.warning(
                            "migration: report number associated with multiple"
                            "recid. See {0}".format(item['recid']))


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@click.option(
    '--source-type',
    '-t',
    type=click.Choice(['json', 'marcxml']),
    default='json',
    help='Whether to use JSON or MARCXML.')
@click.option(
    '--recid',
    '-r',
    help='Record ID to load (NOTE: will load only one record!).',
    default=None)
@click.option(
    '--rectype',
    '-x',
    help='Type of record to load (f.e serial)',
    default=None)
@with_appcontext
def load(sources, source_type, recid, rectype):
    """Load records migration dump."""
    load_records(sources=sources, source_type=source_type, eager=True,
                 rectype=rectype)


@dumps.command()
@click.argument('source', nargs=1, type=click.Path(exists=True))
@click.option(
    '--recid',
    '-r',
    help='Record ID to load (NOTE: will load only one record!).',
    default=None)
@click.option(
    '--rectype',
    '-x',
    help='Type of record to load (f.e serial)',
    default=None)
@with_appcontext
def loadparents(source, recid, rectype):
    """Load records migration dump."""
    if source:
        load_dumps_from_dir(source, rectype=rectype)
    else:
        click.secho('You have to provide source dir', fg='red', bold=True,
                    err=True)
