# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Literature tasks."""

import logging
import urllib

from celery import shared_task
from invenio_app_ils.documents.api import Document
from invenio_db import db

from .covers import build_literature_cover_urls

logger = logging.getLogger('tasks')

# NOTE: Series have covers too
# from invenio_app_ils.records.api import Series


ALLOWED_CLASSES = [Document]
MIN_CONTENT_LENGTH = 128


def update_cover(sender, *args, **kwargs):
    """Triggers async task to update cover metadata of the record."""
    record = kwargs.get("record", {})
    if record.__class__ in ALLOWED_CLASSES:
        update_cover_metadata_isbn.apply_async((record,))


@shared_task(ignore_result=True)
def update_cover_metadata_isbn(record):
    """Update record cover metadata isbn."""
    cover_meta = record.get("cover_metadata", {})
    if cover_meta.get("isbn"):
        return

    identifies = record.get("identifies", [])
    for ident in identifies:
        if ident["schema"] == "ISBN":
            record["cover_metadata"]["isbn"] = ident["value"]
            record.commit()
            db.session.commit()
            return


def set_cover(sender, *args, **kwargs):
    """Triggers async task to set cover metadata of the record."""
    record = kwargs.get("record", {})
    if record.__class__ in ALLOWED_CLASSES:
        set_cover_metadata_isbn.apply_async((record,))


@shared_task(ignore_result=True)
def set_cover_metadata_isbn(record):
    """Set record cover metadata isbn with valid cover."""

    def is_valid_response(response):
        """Validates if the syndetic response returned a cover."""
        # NOTE: When there is no cover, syndetic returns a 1x1 pixel image
        if (
            response.getcode() == 200 and
            response.get("Content-Length") > MIN_CONTENT_LENGTH
        ):
            return True
        return False

    # 1. try if existing cover_metadata are valid
    cover_meta = record.get("cover_metadata", {})
    if cover_meta.get("isbn"):
        url = build_literature_cover_urls(record)['small']
        try:
            resp = urllib.request.urlopen(url)
            if is_valid_response(resp):
                return
        except Exception as e:
            logger.exception(e)

    # 2. assign the first valid isbn identifier
    identifies = record.get("identifies", [])
    for ident in identifies:
        if ident["schema"] == "ISBN":
            record["cover_metadata"]["isbn"] = ident["value"]
            url = build_literature_cover_urls(record)['small']
            try:
                resp = urllib.request.urlopen(url)
                if is_valid_response(resp):
                    record.commit()
                    db.session.commit()
                    return
            except Exception as e:
                logger.exception(e)
