#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

pydocstyle cds_ils tests docs && \
isort cds_ils tests --check --diff && \
check-manifest --ignore ".travis-*,docs/_build*" && \
sphinx-build -qnNW docs docs/_build/html && \
pytest tests/
