# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CLI for CDS-ILS."""

import json
import os
import pathlib
import random
from datetime import timedelta
from random import randint

import arrow
import click
import pkg_resources
from flask import current_app
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_app_ils.circulation.search import get_active_loan_by_item_pid
from invenio_app_ils.cli import minter
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE
from invenio_app_ils.indexer import wait_es_refresh
from invenio_app_ils.items.api import ITEM_PID_TYPE
from invenio_app_ils.locations.api import LOCATION_PID_TYPE
from invenio_app_ils.proxies import current_app_ils
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_base.app import create_cli
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from invenio_circulation.proxies import current_circulation
from invenio_db import db
from invenio_pages import Page
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records import Record
from invenio_search import current_search
from invenio_search.engine import dsl
from invenio_userprofiles import UserProfile

from cds_ils.literature.tasks import pick_identifier_with_cover_task

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()


@click.group()
def fixtures():
    """Create initial data and demo records."""


@click.group()
def covers():
    """Covers scripts group."""


@fixtures.command()
@with_appcontext
def pages():
    """Register CDS static pages."""

    def page_data(page):
        return (
            pkg_resources.resource_stream("cds_ils", os.path.join("static_pages", page))
            .read()
            .decode("utf8")
        )

    pages = [
        Page(
            url="/about",
            title="About",
            description="About",
            content=page_data("about.html"),
            template_name="invenio_pages/dynamic.html",
        ),
        Page(
            url="/terms",
            title="Terms and Conditions",
            description="Terms and Conditions",
            content=page_data("terms.html"),
            template_name="invenio_pages/dynamic.html",
        ),
        Page(
            url="/faq",
            title="F.A.Q.",
            description="F.A.Q.",
            content=page_data("faq.html"),
            template_name="invenio_pages/dynamic.html",
        ),
        Page(
            url="/contact",
            title="Contact",
            description="Contact",
            content=page_data("contact.html"),
            template_name="invenio_pages/dynamic.html",
        ),
        Page(
            url="/guide/search",
            title="Search guide",
            description="Search guide",
            content=page_data("search_guide.html"),
            template_name="invenio_pages/dynamic.html",
        ),
        Page(
            url="/privacy-policy",
            title="Privacy Policy",
            description="Privacy Policy",
            content=page_data("privacy_policy.html"),
            template_name="invenio_pages/dynamic.html",
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
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    closed = ["saturday", "sunday"]
    times = [
        {"start_time": "08:30", "end_time": "18:00"},
    ]
    opening_weekdays = []
    for weekday in weekdays:
        is_open = weekday not in closed
        opening_weekdays.append(
            {
                "weekday": weekday,
                "is_open": weekday not in closed,
                **({"times": times} if is_open else {}),
            }
        )
    location = {
        "pid": RecordIdProviderV2.create().pid.pid_value,
        "name": "CERN Library",
        "address": "Rue de Meyrin",
        "email": "library.desk@cern.ch",
        "opening_weekdays": opening_weekdays,
        "opening_exceptions": [],
    }
    record = current_app_ils.location_record_cls.create(location)
    minter(LOCATION_PID_TYPE, "pid", record)
    db.session.commit()
    current_app_ils.location_indexer.index(record)


def create_userprofile_for(email, username, full_name):
    """Create a fake user profile."""
    user = User.query.filter_by(email=email).one_or_none()
    if user:
        profile = UserProfile(user_id=int(user.get_id()))
        profile.username = username
        profile.full_name = full_name
        db.session.add(profile)
        db.session.commit()
        click.secho("User profile created for {}".format(email), fg="green")
    else:
        click.secho("ERROR: user {} does not exist".format(email), fg="red")


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
    create_userprofile_for("patron1@test.ch", "patron1", "VILMA, Yannic")
    run_command("users create patron2@test.ch -a --password=123456")  # ID 2
    create_userprofile_for("patron2@test.ch", "patron2", "ADI, Diana")
    run_command("users create admin@test.ch -a --password=123456")  # ID 3
    create_userprofile_for("admin@test.ch", "admin", "RYOICHI, Zeki")
    run_command("users create librarian@test.ch -a --password=123456")  # ID 4
    create_userprofile_for("librarian@test.ch", "librarian", "NABU, Hector")
    run_command("users create patron3@test.ch -a --password=123456")  # ID 5
    create_userprofile_for("patron3@test.ch", "patron3", "TARA, Medrod")
    run_command("users create patron4@test.ch -a --password=123456")  # ID 6
    create_userprofile_for("patron4@test.ch", "patron4", "CUPID, Devi")

    # Assign roles
    run_command("roles add admin@test.ch admin")
    run_command("roles add librarian@test.ch librarian")

    # Assign actions
    run_command("access allow superuser-access role admin")
    run_command("access allow ils-backoffice-access role librarian")

    run_command("patrons index")


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

    # licenses
    run_command("vocabulary index opendefinition spdx --force")
    run_command("vocabulary index opendefinition opendefinition --force")
    # languages
    run_command("vocabulary index languages --force")

    # keep JSON files as last. Extra licenses will be added to the ones
    # imported above
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


def recreate_cover(pid, record_class):
    """Recreate cover for a given record pid."""
    record = record_class.get_record_by_pid(pid)
    if record:
        pick_identifier_with_cover_task(record)
        click.secho("Recreated cover for PID: {}".format(pid), fg="blue")
    else:
        click.secho("No document or series found with PID: {}", fg="red")


@covers.command()
@click.option("-t", "--pid-type", required=True, type=click.Choice(["docid", "serid"]))
@click.option("-a", "--all", required=False, is_flag=True)
@click.option("-p", "--pid")
@with_appcontext
def recreate(pid, pid_type, all):
    """Recreate covers command."""
    if pid_type == DOCUMENT_PID_TYPE:
        record_class = current_app_ils.document_record_cls
    elif pid_type == SERIES_PID_TYPE:
        record_class = current_app_ils.series_record_cls
    if all:
        pid_list = (
            PersistentIdentifier.query.filter_by(
                object_type="rec", status=PIDStatus.REGISTERED
            )
            .filter(PersistentIdentifier.pid_type == pid_type)
            .values(PersistentIdentifier.pid_value)
        )
        pid_values = [pid[0] for pid in pid_list]
        for pid_entry in pid_values:
            recreate_cover(pid_entry, record_class)
    else:
        recreate_cover(pid, record_class)


@click.group()
def user_testing():
    """Create real demo data for user testing."""


def mint_record_pid(pid_type, pid_field, record):
    """Mint the given PID for the given record."""
    PersistentIdentifier.create(
        pid_type=pid_type,
        pid_value=record[pid_field],
        object_type="rec",
        object_uuid=record.id,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()


@user_testing.command()
@click.option("--json-path", "docs_path")
@with_appcontext
def create_demo_docs(docs_path):
    """Insert real demo docs."""
    demo_docs = os.path.join(CURRENT_DIR, docs_path)
    with open(os.path.join(demo_docs)) as f:
        demo_data = json.loads(f.read())

    for d in demo_data:
        doc = current_app_ils.document_record_cls.create(d)
        mint_record_pid(DOCUMENT_PID_TYPE, "pid", doc)
        current_app_ils.document_indexer.index(doc)

    click.secho("Docs were created successfully.", fg="blue")


def get_pids(search):
    """Get a list of pids of the search results."""
    pids = []
    for hit in search().scan():
        pids.append(hit["pid"])

    return pids


@user_testing.command()
@click.option("--json-path", "items_path")
@with_appcontext
def create_demo_items(items_path):
    """Insert real demo items."""
    demo_items = os.path.join(CURRENT_DIR, items_path)
    with open(os.path.join(demo_items)) as f:
        demo_items = json.loads(f.read())

    intloc_pids = get_pids(current_app_ils.internal_location_search_cls)

    for i in demo_items:
        i["internal_location_pid"] = random.choice(intloc_pids)
        item = current_app_ils.item_record_cls.create(i)
        mint_record_pid(ITEM_PID_TYPE, "pid", item)
        current_app_ils.item_indexer.index(item)

    click.secho("Items were created successfully.", fg="blue")


@user_testing.command()
@click.option("--user-email", "user_email")
@click.option("--is-past-loan", is_flag=True)
@with_appcontext
def create_loan(user_email, is_past_loan):
    """Create a loan."""
    # hardcode doc/item pids from the demo_data jsons
    ongoing_loan_item_pid = "vgrh9-jvj8E"
    past_loan_item_pid = "678e3-an678A"
    ongoing_loan_doc_pid = "67186-5rs9E"
    past_loan_doc_pid = "qaywb-gfe4B"

    active_loan = (
        get_active_loan_by_item_pid({"type": "pitmid", "value": ongoing_loan_item_pid})
        .execute()
        .hits
    )

    total = active_loan.total.value

    if total > 0 and not is_past_loan:
        click.secho(
            "Item for ongoing loan is already loaned by patron with email {0}.".format(
                active_loan[0].patron.email
            ),
            fg="red",
        )
        return

    patron = User.query.filter_by(email=user_email).one()
    patron_pid = patron.get_id()

    loc_pid, _ = current_app_ils.get_default_location_pid

    delivery = list(current_app.config["ILS_CIRCULATION_DELIVERY_METHODS"].keys())[
        randint(0, 1)
    ]

    loan_dict = {
        "pid": RecordIdProviderV2.create().pid.pid_value,
        "patron_pid": "{}".format(patron_pid),
        "pickup_location_pid": "{}".format(loc_pid),
        "transaction_location_pid": "{}".format(loc_pid),
        "transaction_user_pid": "{}".format(patron_pid),
        "delivery": {"method": delivery},
    }

    if is_past_loan:
        loan_dict["state"] = "ITEM_RETURNED"
        loan_dict["document_pid"] = past_loan_doc_pid
        transaction_date = start_date = arrow.utcnow() - timedelta(days=365)
        end_date = start_date + timedelta(weeks=4)
        item_pid = past_loan_item_pid
    else:
        loan_dict["state"] = "ITEM_ON_LOAN"
        loan_dict["document_pid"] = ongoing_loan_doc_pid
        transaction_date = start_date = arrow.utcnow() - (
            timedelta(weeks=4)
            - timedelta(
                days=current_app.config["ILS_CIRCULATION_LOAN_WILL_EXPIRE_DAYS"]
            )
        )
        end_date = start_date + timedelta(weeks=4)
        item_pid = ongoing_loan_item_pid

    loan_dict["transaction_date"] = transaction_date.isoformat()
    loan_dict["start_date"] = start_date.date().isoformat()
    loan_dict["end_date"] = end_date.date().isoformat()
    loan_dict["extension_count"] = randint(0, 3)
    loan_dict["item_pid"] = {"type": ITEM_PID_TYPE, "value": item_pid}

    loan = current_circulation.loan_record_cls.create(loan_dict)
    minter(CIRCULATION_LOAN_PID_TYPE, "pid", loan)
    db.session.commit()
    current_circulation.loan_indexer().index(loan)
    item = current_app_ils.item_record_cls.get_record_by_pid(item_pid)
    current_app_ils.item_indexer.index(item)

    current_search.flush_and_refresh(index="*")

    doc = current_app_ils.document_record_cls.get_record_by_pid(
        loan_dict["document_pid"]
    )

    click.secho(
        "Loan with pid '{0}' on document '{1}' was created.".format(
            loan_dict["pid"], doc["title"]
        ),
        fg="blue",
    )


@user_testing.command()
@click.option("--user-email", "user_email")
@click.option("--given-date", "given_date")
@with_appcontext
def clean_loans(user_email, given_date):
    """Clean loans and doc requests created by given user on given date."""
    patron = User.query.filter_by(email=user_email).one()
    patron_pid = patron.get_id()

    patron_document_requests = (
        current_app_ils.document_request_search_cls()
        .filter(
            "bool",
            filter=[
                dsl.Q("term", patron_pid=patron_pid),
                dsl.Q("term", _created=given_date),
            ],
        )
        .scan()
    )

    for hit in patron_document_requests:
        document_request = (
            current_app_ils.document_request_record_cls.get_record_by_pid(hit.pid)
        )
        document_request.delete(force=True)
        db.session.commit()
        current_app_ils.document_request_indexer.delete(document_request)

    patron_loans = (
        current_circulation.loan_search_cls()
        .filter(
            "bool",
            filter=[
                dsl.Q("term", patron_pid=patron_pid),
                dsl.Q("term", _created=given_date),
            ],
        )
        .scan()
    )

    for hit in patron_loans:
        loan = current_circulation.loan_record_cls.get_record_by_pid(hit.pid)
        loan.delete(force=True)
        db.session.commit()
        current_circulation.loan_indexer().delete(loan)
        if "item_pid" in loan:
            item = current_app_ils.item_record_cls.get_record_by_pid(
                loan["item_pid"]["value"]
            )
            loan_index = current_circulation.loan_search_cls.Meta.index
            wait_es_refresh(loan_index)
            current_app_ils.item_indexer.index(item)

    current_search.flush_and_refresh(index="*")

    click.secho(
        "Loans and document requests of user with pid '{0}' have been deleted.".format(
            patron_pid
        ),
        fg="blue",
    )


@user_testing.command()
@click.option("--path", help="Json filepath for demo data.")
@click.option("--are-docs", is_flag=True, help="Importing docs.")
@click.option("--are-items", is_flag=True, help="Importing items.")
@click.option("--verbose", is_flag=True, help="Verbose output.")
@with_appcontext
def import_demo_data(path, are_docs, are_items, verbose):
    """Import real demo data."""
    cli = create_cli()
    runner = current_app.test_cli_runner()

    def run_command(command, catch_exceptions=False):
        click.secho("cds-ils {}...".format(command), fg="green")
        res = runner.invoke(cli, command, catch_exceptions=catch_exceptions)
        if verbose:
            click.secho(res.output)

    if are_docs:
        command = "create-demo-docs"
    elif are_items:
        command = "create-demo-items"

    run_command("user-testing " + command + " --json-path " + path)


@user_testing.command()
@click.option("--user-email", help="User to have a loan on the book.")
@click.option("--verbose", is_flag=True, help="Verbose output.")
@with_appcontext
def prepare(user_email, verbose):
    """Create loans for user."""
    cli = create_cli()
    runner = current_app.test_cli_runner()

    def run_command(command, catch_exceptions=False):
        click.secho("cds-ils {}...".format(command), fg="green")
        res = runner.invoke(cli, command, catch_exceptions=catch_exceptions)
        if verbose:
            click.secho(res.output)

    # create ongoing loan
    run_command("user-testing create-loan  --user-email " + user_email)

    # create past loan
    run_command("user-testing create-loan --is-past-loan --user-email " + user_email)


@user_testing.command()
@click.option("--user-email", help="User to delete all of the loans they created.")
@click.option(
    "--given-date",
    help="All loans created on this day by the user will be deleted.",
)
@click.option("--verbose", is_flag=True, help="Verbose output.")
@with_appcontext
def clean(user_email, given_date, verbose):
    """Remove loans of user."""
    cli = create_cli()
    runner = current_app.test_cli_runner()

    def run_command(command, catch_exceptions=False):
        click.secho("cds-ils {}...".format(command), fg="green")
        res = runner.invoke(cli, command, catch_exceptions=catch_exceptions)
        if verbose:
            click.secho(res.output)

    if not given_date:
        given_date = arrow.utcnow().format("YYYY-MM-DD")

    run_command(
        "user-testing clean-loans --user-email "
        + user_email
        + " --given-date "
        + given_date
    )


@click.group()
def maintenance():
    """Maintenance commands."""


@maintenance.command()
@click.option("-p", "--pid")
@with_appcontext
def revert_delete_record(pid):
    """Reverts deletion action of a record."""
    pid_obj = PersistentIdentifier.query.filter_by(pid_value=pid).one()

    record_uuid = pid_obj.object_uuid
    deleted = Record.get_record(record_uuid, with_deleted=True)

    if not deleted.is_deleted:
        click.secho(f"Record {pid} was not deleted. Aborting.", fg="red")
        return

    # revert to previous revision
    record = deleted.revert(deleted.revision_id - 1)

    all_pid_objects = PersistentIdentifier.query.filter_by(object_uuid=record_uuid)

    # trying to get all the pid types (including legacy pids)
    for pid_object in all_pid_objects:
        pid_object.status = PIDStatus.REGISTERED

    db.session.commit()

    indexer_class = current_app_ils.indexer_by_pid_type(pid_obj.pid_type)
    indexer_class.index(record)
    click.secho(f"Record {pid} is reverted from deletion.", fg="green")


@maintenance.command()
@click.option("-p", "--pid")
@click.option("-l", "--legacy-pid")
@click.option("-t", "--legacy-pid-type")
@with_appcontext
def assign_legacy_pid(pid, legacy_pid, legacy_pid_type):
    """Assign legacy pid to given record."""
    doc_legacy_pid_cfg = current_app.config["CDS_ILS_RECORD_LEGACY_PID_TYPE"]
    series_legacy_pid_cfg = current_app.config["CDS_ILS_SERIES_LEGACY_PID_TYPE"]

    if legacy_pid_type not in [doc_legacy_pid_cfg, series_legacy_pid_cfg]:
        click.secho("Invalid legacy pid type", fg="red")
        return

    pid_obj = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value == pid
    ).one()

    is_document = pid_obj.pid_type == DOCUMENT_PID_TYPE
    is_series = pid_obj.pid_type == SERIES_PID_TYPE
    is_legacy_document = legacy_pid_type == doc_legacy_pid_cfg
    is_legacy_series = legacy_pid_type == series_legacy_pid_cfg

    if is_legacy_document and not is_document:
        click.secho(
            "Pid types mismatch. " "You are trying to assign ldocid to series record",
            fg="red",
        )
        return
    if is_legacy_series and not is_series:
        click.secho(
            "Pid types mismatch. " "You are trying to assign lserid to document record",
            fg="red",
        )
        return

    PersistentIdentifier.create(
        pid_type=legacy_pid_type,
        pid_value=str(legacy_pid),
        object_type="rec",
        object_uuid=pid_obj.object_uuid,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()
