# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Importer xml parser module."""
from flask import current_app
from lxml import etree


def get_records_list(xml_file):
    """Generate list of isolated records."""
    record_tag_path = current_app.config["CDS_ILS_IMPORTER_RECORD_TAG"]

    root = etree.parse(xml_file).getroot()
    # namespaced XMLs
    for record in root.xpath(record_tag_path):
        yield record
