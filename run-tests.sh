#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services
function cleanup() {
  eval "$(docker-services-cli down --env)"
}
trap cleanup EXIT
python -m check_manifest
eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${SEARCH:-opensearch2} --cache ${CACHE:-redis} --env)"
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
