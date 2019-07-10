# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Books ldap users CLI."""

from __future__ import absolute_import, print_function

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount
from sqlalchemy.orm.exc import NoResultFound

from .api import LdapClient, LdapUserImporter


def import_ldap_users(ldap_users):
    """Import ldap users in db."""
    importer = LdapUserImporter(ldap_users)
    importer.import_users()


def check_user_for_update(system_user, ldap_user):
    """Check if there is an ldap update for a user and commit changes."""
    ldap_user_department = ldap_user["department"][0].decode("utf8")
    if not system_user.extra_data["department"] == ldap_user_department:
        click.secho("Changes detected for system user {}".format(
            str(system_user.user)), fg="green")
        click.secho(
            "System user's department {} is different than the {}".format(
                system_user.extra_data["department"], ldap_user_department),
            fg="green")
        system_user.extra_data.update(dict(department=ldap_user_department))
        db.session.commit()


def delete_user(system_user):
    """Delete a system user."""
    pass


@click.group()
def ldap_users():
    """Ldap users import CLI."""


@ldap_users.command(name="import")
@with_appcontext
def import_users():
    """Load users from ldap and import them in db."""
    import time
    start_time = time.time()

    ldap_url = current_app.config["CDS_BOOKS_LDAP_URL"]
    ldap_client = LdapClient(ldap_url)
    ldap_users = ldap_client.get_primary_accounts()

    click.secho("Users found {}".format(len(ldap_users)))

    import_ldap_users(ldap_users)

    click.secho(
        "--- Finished in %s seconds ---" % (time.time() - start_time),
        fg="green"
    )


@ldap_users.command(name="sync")
@with_appcontext
def sync_users():
    """Sync ldap with system users command."""
    import time
    start_time = time.time()

    ldap_url = current_app.config["CDS_BOOKS_LDAP_URL"]
    ldap_client = LdapClient(ldap_url)
    system_users = RemoteAccount.query.join(User).all()
    ldap_users = ldap_client.get_primary_accounts()

    click.echo("Users fetched")

    ldap_users_map = {}

    for ldap_user in ldap_users:
        ldap_person_id = ldap_user["employeeID"][0].decode("utf8")
        ldap_users_map.update({ldap_person_id: ldap_user})

    for system_user in system_users:
        system_user_person_id = system_user.extra_data["person_id"]
        ldap_user = ldap_users_map.get(system_user_person_id)
        if ldap_user:
            check_user_for_update(system_user, ldap_user)
        else:
            click.secho("Deleting user {} with ccid {}".format(
                system_user.user, system_user_person_id), fg="red")
            delete_user(system_user)

    # Check if any ldap user is not in our system

    for ldap_user in ldap_users:
        ldap_mail = ldap_user["mail"][0].decode("utf8")
        try:
            User.query.filter(User.email == ldap_mail).one()
        except NoResultFound:
            click.secho("Adding new user {}".format(ldap_mail), fg="green")
            import_ldap_users([ldap_user])

    click.secho(
        "--- Finished in %s seconds ---" % (time.time() - start_time),
        fg="green"
    )
