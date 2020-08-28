# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for theme."""

from flask_webpackext import WebpackBundle

theme = WebpackBundle(
    __name__,
    'assets',
    entry={
        'cds-ils-theme': './scss/cds_ils/theme.scss',
    },
    dependencies={
        # add any additional npm dependencies here...
    }
)
