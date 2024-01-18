# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import json
import logging

import click
from flask import current_app
from invenio_app_ils.patrons.indexer import PatronIndexer
from invenio_app_ils.patrons.search import PatronsSearch
from invenio_db import db
from invenio_oauthclient.models import RemoteAccount
from invenio_search.engine import dsl

from cds_ils.migrator.errors import UserMigrationError
from cds_ils.patrons.api import Patron

migrated_logger = logging.getLogger("migrated_records")


def import_users_from_json(dump_file):
    """Imports additional user data from JSON."""
    dump_file = dump_file[0]
    with click.progressbar(json.load(dump_file)) as bar:
        for record in bar:
            click.echo(
                'Importing user "{0}({1})"...'.format(record["id"], record["email"])
            )
            ccid = record.get("ccid")
            if not ccid:
                click.secho(
                    "User {0}({1}) does not have ccid".format(
                        record["id"], record["email"]
                    ),
                    fg="magenta",
                )
                continue
            user = get_user_by_person_id(ccid)
            if not user:
                click.secho(
                    "User {0}({1}) not synced via LDAP".format(
                        record["id"], record["email"]
                    ),
                    fg="yellow",
                )
                continue
                # todo uncomment when more data
                # raise UserMigrationError
            else:
                client_id = current_app.config["CERN_APP_OPENID_CREDENTIALS"][
                    "consumer_key"
                ]
                account = RemoteAccount.get(user_id=user.id, client_id=client_id)
                extra_data = account.extra_data
                if "legacy_id" in extra_data:
                    del extra_data["legacy_id"]
                # add legacy_id information
                account.extra_data.update(legacy_id=str(record["id"]), **extra_data)
                db.session.add(account)
                patron = Patron(user.id)
                PatronIndexer().index(patron)
        db.session.commit()


def get_user_by_person_id(person_id):
    """Get ES object of the patron."""
    search = PatronsSearch().query(
        "bool",
        filter=[
            dsl.Q("term", person_id=person_id),
        ],
    )
    results = search.execute()
    hits_total = results.hits.total.value
    if not results.hits or hits_total < 1:
        click.secho("no user found with person_id {}".format(person_id), fg="red")
        return None
    elif hits_total > 1:
        raise UserMigrationError(
            "found more than one user with person_id {}".format(person_id)
        )
    else:
        return results.hits[0]


def get_user_by_legacy_id(legacy_id):
    """Get ES object of the patron."""
    search = PatronsSearch().query(
        "bool",
        filter=[
            dsl.Q("term", legacy_id=legacy_id),
        ],
    )
    results = search.execute()
    hits_total = results.hits.total.value
    if not results.hits or hits_total < 1:
        click.secho("no user found with legacy_id {}".format(legacy_id), fg="red")
        return None
    elif hits_total > 1:
        raise UserMigrationError(
            "found more than one user with legacy_id {}".format(legacy_id)
        )
    else:
        return results.hits[0]
