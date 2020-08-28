#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

pipenv run pydocstyle cds_ils tests docs && \
pipenv run isort . --check --diff && \
pipenv run check-manifest --ignore ".travis-*,docs/_build*" && \
pipenv run sphinx-build -qnNW docs docs/_build/html && \
pipenv run test
