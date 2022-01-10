# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS ldap users CLI."""

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db

from .api import delete_users as ldap_delete_users
from .api import import_users as ldap_import_users
from .api import update_users as ldap_update_users
from .models import LdapSynchronizationLog


@click.group()
def ldap_users():
    """Ldap users import CLI."""


@ldap_users.command(name="import")
@with_appcontext
def import_users():
    """Load users from LDAP and import them in DB."""
    ldap_import_users()


@ldap_users.command(name="update")
@with_appcontext
def update_users():
    """Load users from LDAP and import new ones or update existing in DB."""
    log = LdapSynchronizationLog.create_cli()
    try:
        result = ldap_update_users()
        log.set_succeeded(*result)
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(e)
        log.set_failed(e)


@ldap_users.command(name="delete")
@with_appcontext
def delete_users():
    """Load users from LDAP and delete the ones that are still in the DB."""
    try:
        ldap_delete_users(mark_for_deletion=False)
    except Exception as e:
        current_app.logger.exception(e)
