# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# cds-migrator-kit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS Migrator Records exceptions."""

from dojson.errors import DoJSONException


class LossyConversion(DoJSONException):
    """Data lost during migration."""

    def __init__(self, *args, **kwargs):
        """Exception custom initialisation."""
        self.missing = kwargs.pop('missing', None)
        self.message = 'Lossy conversion: {0}'.format(self.missing or '')
        super(LossyConversion, self).__init__(*args, **kwargs)
