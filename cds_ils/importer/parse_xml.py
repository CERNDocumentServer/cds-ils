# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer xml parser module."""
from lxml import etree

from cds_ils.importer.config import CDS_ILS_IMPORTER_RECORD_TAG


def get_records_list(xml_file):
    """Generate list of isolated records."""
    root = etree.parse(xml_file).getroot()
    # namespaced XMLs
    for record in root.xpath(CDS_ILS_IMPORTER_RECORD_TAG):
        yield record


def analyze_file(xml_file):
    """Analyze records number."""
    root = etree.parse(xml_file).getroot()
    # namespaced XMLs
    return len(root.xpath(CDS_ILS_IMPORTER_RECORD_TAG))
