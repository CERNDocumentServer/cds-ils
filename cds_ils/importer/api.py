# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer API module."""
import json
import logging

import click
from celery import shared_task
from invenio_app_ils.errors import IlsValidationError
from invenio_db import db

from cds_ils.importer.errors import LossyConversion
from cds_ils.importer.parse_xml import get_records_list
from cds_ils.importer.XMLRecordLoader import XMLRecordDumpLoader
from cds_ils.importer.XMLRecordToJson import XMLRecordToJson

records_logger = logging.getLogger("records_errored")


@shared_task()
def process_dump(data, provider, source_type):
    """Process record dump."""
    recorddump = XMLRecordToJson(
        data,
        source_type=source_type,
    )
    try:
        report = XMLRecordDumpLoader.process(recorddump, provider)
        db.session.commit()
        return report
    except Exception as e:
        db.session.rollback()
        raise e


def import_record(data, provider, source_type=None, eager=False):
    """Import record from dump."""
    source_type = source_type or "marcxml"
    assert source_type in ["marcxml"]

    if eager:
        return process_dump(data, provider, source_type=source_type)
    else:
        process_dump.delay(data, provider, source_type=source_type)


def import_from_xml(sources, source_type, provider, eager=True):
    """Load xml file."""
    records = []
    # TODO: To be removed
    file_name = '/tmp/my_file.json'
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Importing documents in {}...".format(
                idx, len(sources), source.name
            )
        )

        i = 0
        for record in get_records_list(source):
            try:
                click.secho("Processing record {}".format(i))
                i += 1
                report = import_record(
                    record, provider, source_type=source_type, eager=True
                )
                click.secho(
                    "Created: {}\n "
                    "Updated: "
                    "{}\n "
                    "Ambiguous matches {}\n "
                    "Fuzzy matches {}\n".format(
                        report["created"],
                        report["updated"],
                        report["ambiguous_documents"],
                        report["fuzzy"],
                    ),
                    fg="blue",
                )
                records.append(report)
                # TODO: To be removed
                f = open(file_name, 'w+')
                f.writelines([json.dumps(records)])
                f.close()

            except LossyConversion as e:
                continue
            except IlsValidationError as e:
                records_logger.error(
                    "@FILE: {0} FATAL: {1}".format(
                        source.name,
                        str(e.original_exception.message),
                    )
                )
                continue
            except Exception as e:
                records_logger.error(
                    "@FILE: {0} ERROR: {1}".format(source.name, str(e))
                )
                raise e

    return records
