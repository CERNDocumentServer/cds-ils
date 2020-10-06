# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS migrator API."""

import click
from invenio_app_ils.records_relations.api import RecordRelationsParentChild


def create_parent_child_relation(parent, child, relation_type, volume):
    """Create parent child relations."""
    rr = RecordRelationsParentChild()
    click.echo(
        "Creating relations: {0} - {1}".format(parent["pid"], child["pid"])
    )
    rr.add(
        parent=parent,
        child=child,
        relation_type=relation_type,
        volume=str(volume) if volume else None,
    )
