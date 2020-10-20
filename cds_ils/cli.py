# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CLI for CDS-ILS."""
import os

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_app_ils.cli import minter
from invenio_app_ils.locations.api import LOCATION_PID_TYPE, Location
from invenio_app_ils.locations.indexer import LocationIndexer
from invenio_base.app import create_cli
from invenio_db import db
from invenio_pages import Page
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_userprofiles import UserProfile


@click.group()
def fixtures():
    """Create initial data and demo records."""


@fixtures.command()
@with_appcontext
def pages():
    """Register CDS static pages."""
    pages = [
        Page(
            url="/about",
            title="About",
            description="About",
            content="Library about page",
            template_name="invenio_pages/default.html",
        ),
        Page(
            url="/terms",
            title="Terms",
            description="Terms",
            content="Terms and Privacy",
            template_name="invenio_pages/default.html",
        ),
        Page(
            url="/faq",
            title="F.A.Q.",
            description="F.A.Q.",
            content="Frequently Asked Questions",
            template_name="invenio_pages/default.html",
        ),
    ]
    with db.session.begin_nested():
        Page.query.delete()
        db.session.add_all(pages)
    db.session.commit()
    click.echo("static pages created :)")


@fixtures.command()
@with_appcontext
def location():
    """Create library location."""
    click.echo("Creating locations...")
    location = {
        "pid": RecordIdProviderV2.create().pid.pid_value,
        "name": "CERN Central Library",
        "address": "Rue de Meyrin",
        "email": "library@cern.ch",
    }
    record = Location.create(location)
    minter(LOCATION_PID_TYPE, "pid", record)
    record.commit()
    db.session.commit()
    indexer = LocationIndexer()
    indexer.index(record)


def create_userprofile_for(email, username, full_name):
    """Create a fake user profile."""
    user = User.query.filter_by(email=email).one_or_none()
    if user:
        profile = UserProfile(user_id=int(user.get_id()))
        profile.username = username
        profile.full_name = full_name
        db.session.add(profile)
        db.session.commit()


@fixtures.command()
@with_appcontext
def demo_patrons():
    """Create demo patrons."""
    cli = create_cli()
    runner = current_app.test_cli_runner()

    def run_command(command, catch_exceptions=False, verbose=True):
        click.secho("ils {}...".format(command), fg="green")
        res = runner.invoke(cli, command, catch_exceptions=catch_exceptions)
        if verbose:
            click.secho(res.output)

    # Create roles to restrict access
    run_command("roles create admin")
    run_command("roles create librarian")

    # Create users
    run_command("users create patron1@test.ch -a --password=123456")  # ID 1
    create_userprofile_for("patron1@test.ch", "patron1", "Yannic Vilma")
    run_command("users create patron2@test.ch -a --password=123456")  # ID 2
    create_userprofile_for("patron2@test.ch", "patron2", "Diana Adi")
    run_command("users create admin@test.ch -a --password=123456")  # ID 3
    create_userprofile_for("admin@test.ch", "admin", "Zeki Ryoichi")
    run_command("users create librarian@test.ch -a --password=123456")  # ID 4
    create_userprofile_for("librarian@test.ch", "librarian", "Hector Nabu")
    run_command("users create patron3@test.ch -a --password=123456")  # ID 5
    create_userprofile_for("patron3@test.ch", "patron3", "Medrod Tara")
    run_command("users create patron4@test.ch -a --password=123456")  # ID 6
    create_userprofile_for("patron4@test.ch", "patron4", "Devi Cupid")

    # Assign roles
    run_command("roles add admin@test.ch admin")
    run_command("roles add librarian@test.ch librarian")

    # Assign actions
    run_command("access allow superuser-access role admin")
    run_command("access allow ils-backoffice-access role librarian")


@fixtures.command()
@with_appcontext
def vocabularies():
    """Create vocabularies fake records."""
    cli = create_cli()
    runner = current_app.test_cli_runner()

    def run_command(command, catch_exceptions=False, verbose=True):
        click.secho("ils {}...".format(command), fg="green")
        res = runner.invoke(cli, command, catch_exceptions=catch_exceptions)
        if verbose:
            click.secho(res.output)

    vocabularies_dir = os.path.join(
        os.path.realpath("."),
        "cds_ils",
        "vocabularies",
        "data",
    )
    json_files = " ".join(
        os.path.join(vocabularies_dir, name)
        for name in os.listdir(vocabularies_dir)
        if name.endswith(".json")
    )
    run_command("vocabulary index json --force {}".format(json_files))
    run_command("vocabulary index opendefinition spdx --force")
    run_command("vocabulary index opendefinition opendefinition --force")
