# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer tasks."""
from celery import shared_task

from cds_ils.importer.api import import_from_xml


@shared_task
def import_from_xml_task(log_id, source_path, source_type, provider, mode):
    """Load a single xml file task."""
    import_from_xml(log_id, source_path, source_type, provider, mode)
