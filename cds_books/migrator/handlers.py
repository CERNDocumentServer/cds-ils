# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records logging handler."""

import logging

logger = logging.getLogger('migrator')


def migration_exception_handler(exc, output, key, value, **kwargs):
    """Migration exception handling - log to files.

    :param exc: exception
    :param output: generated output version
    :param key: MARC field ID
    :param value: MARC field value
    :return:
    """
    logger.error(
        '#RECID: #{0} - {1}  MARC FIELD: *{2}*, input value: {3}, -> {4}, '
        .format(output['recid'], exc.message, key, value, output)
    )
