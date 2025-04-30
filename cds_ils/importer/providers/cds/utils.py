# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Importer Records utils."""
from flask import current_app


def add_title_from_conference_info(json_data):
    """Use the conference info to add a title if it doesn't exist."""
    if (
        json_data["document_type"] in ["PROCEEDINGS", "SERIAL_ISSUE"]
        and "title" not in json_data
    ):
        conference_title = json_data["_migration"].get("conference_title", None)
        if conference_title:
            json_data["title"] = conference_title


def add_cds_url(json_data):
    """Add url pointing back to CDS."""
    _urls = json_data.get("urls", [])

    if json_data.get("sync", False):
        legacy_recid = json_data.get("legacy_recid")

        if legacy_recid:
            _urls.append(
                {
                    "value": f"https://cds.cern.ch/record/{legacy_recid}",
                    "description": "See on CDS",
                    "meta": "CDS",
                }
            )
        del json_data["sync"]

    rdm_pid = json_data.get("_rdm_pid")

    if rdm_pid:
        _urls.append(
            {
                "value": f"{current_app.config['CDS_ILS_CDS_RDM_URI']}/records/{rdm_pid}",
                "description": "See on CDS",
                "meta": "CDS",
            }
        )
    json_data["urls"] = _urls
