# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records utils."""
from flask import current_app

from cds_ils.migrator.errors import ItemMigrationError


def process_fireroles(fireroles):
    """Extract firerole definitions."""
    rigths = set()
    for firerole in fireroles:
        for (allow, not_, field, expressions_list) in firerole[1]:
            if not allow:
                current_app.logger.warning(
                    'Not possible to migrate deny rules: {0}.'.format(
                        expressions_list))
                continue
            if not_:
                current_app.logger.warning(
                    'Not possible to migrate not rules: {0}.'.format(
                        expressions_list))
                continue
            if field in ('remote_ip', 'until', 'from'):
                current_app.logger.warning(
                    'Not possible to migrate {0} rule: {1}.'.format(
                        field, expressions_list))
                continue
            # We only deal with allow group rules
            for reg, expr in expressions_list:
                if reg:
                    current_app.logger.warning(
                        'Not possible to migrate groups based on regular'
                        ' expressions: {0}.'.format(expr))
                    continue
                clean_name = expr[
                             :-len(' [CERN]')].lower().strip().replace(' ',
                                                                       '-')
                rigths.add('{0}@cern.ch'.format(clean_name))
    return rigths


def update_access(data, *access):
    """Merge access rights information.

    :params data: current JSON structure with metadata and potentially an
        `_access` key.
    :param *access: List of dictionaries to merge to the original data, each of
        them in the form `action: []`.
    """
    current_rules = data.get('_access', {})
    for a in access:
        for k, v in a.items():
            current_x_rules = set(current_rules.get(k, []))
            current_x_rules.update(v)
            current_rules[k] = list(current_x_rules)

    data['_access'] = current_rules


def clean_circulation_restriction(record):
    """Translates circulation restrictions of the item."""
    record["circulation_restriction"] = "NO_RESTRICTION"
    if "loan_period" in record:
        options = {
            "1 week": "ONE_WEEK",
            "4 weeks": "NO_RESTRICTION"
        }
        if record["loan_period"].lower() == "reference":
            record["status"] = "FOR_REFERENCE_ONLY"
        elif record["loan_period"] == '':
            record["circulation_restriction"] = "NO_RESTRICTION"
        else:
            try:
                record["circulation_restriction"] = options[
                    record["loan_period"]]
            except KeyError:
                raise ItemMigrationError(
                    "Unknown circulation restriction (loan period) on "
                    "barcode {0}: {1}".format(record["barcode"],
                                              record['loan_period']))
        del record["loan_period"]


def clean_item_status(record):
    """Translates item statuses."""
    # possible values:
    #   on shelf, missing, on loan, in binding, on order,
    #   out of print, not published, not arrived, under review
    options = {
        "on shelf": "CAN_CIRCULATE",
        "missing": "MISSING",
        "on loan": "CAN_CIRCULATE",
        "in binding": "IN_BINDING",
        "FOR_REFERENCE_ONLY": "FOR_REFERENCE_ONLY"
    }
    try:
        record["status"] = options[record["status"]]
    except KeyError:
        raise ItemMigrationError(
            "Unknown item status {0} on barcode {1}".format(
                record["status"], record["barcode"]))


def clean_description_field(record):
    """Cleans the item description."""
    if record["description"] == '-' or record["description"] is None:
        del record["description"]


def clean_item_record(record):
    """Clean the item record object."""
    clean_circulation_restriction(record)
    clean_item_status(record)
    clean_description_field(record)
    record["shelf"] = record["location"]
    record["medium"] = "NOT_SPECIFIED"
    del record["location"]
    del record["id_bibrec"]
    del record["id_crcLIBRARY"]
