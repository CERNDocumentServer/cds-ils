# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CLI for CDS Books."""

import click
import redis
from flask import current_app
from flask.cli import with_appcontext
from invenio_app_ils.cli import minter
from invenio_app_ils.locations.api import LOCATION_PID_TYPE, Location
from invenio_app_ils.locations.indexer import LocationIndexer
from invenio_base.app import create_cli
from invenio_db import db
from invenio_pages import Page
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


@click.group()
def fixtures():
    """Create initial data and demo records."""


@fixtures.command()
@with_appcontext
def pages():
    """Register CDS static pages."""
    pages = [
        Page(url='/about',
             title='About',
             description='About',
             content='Library about page',
             template_name='invenio_pages/default.html'),
        Page(url='/terms',
             title='Terms',
             description='Terms',
             content='Terms and Privacy',
             template_name='invenio_pages/default.html'),
        Page(url='/faq',
             title='F.A.Q.',
             description='F.A.Q.',
             content='Frequently Asked Questions',
             template_name='invenio_pages/default.html'),
    ]
    with db.session.begin_nested():
        Page.query.delete()
        db.session.add_all(pages)
    db.session.commit()
    click.echo('static pages created :)')


@fixtures.command()
@with_appcontext
def location():
    """Create library location."""
    click.echo("Creating locations...")
    location = {
        "pid": RecordIdProviderV2.create().pid.pid_value,
        "name": "CERN Central Library",
        "address": "Rue de Meyrin",
        "email": "library@cern.ch"
    }
    record = Location.create(location)
    minter(LOCATION_PID_TYPE, "pid", record)
    record.commit()
    db.session.commit()
    indexer = LocationIndexer()
    indexer.index(record)
