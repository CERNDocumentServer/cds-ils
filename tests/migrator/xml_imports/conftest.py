# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""Pytest fixtures for xml imports."""

from os.path import dirname, join

import pytest


@pytest.fixture()
def datadir():
    """Get data directory."""
    return join(dirname(__file__), "data")
