# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS Importer serializers."""

from cds_ils.importer.serializers.response import (
    importer_task_log_responsify,
    importer_task_responsify,
)
from cds_ils.importer.serializers.schema import (
    ImporterTaskDetailLogV1,
    ImporterTaskLogV1,
)

task_entry_response = importer_task_responsify(
    ImporterTaskDetailLogV1, "application/json"
)

task_log_response = importer_task_log_responsify(ImporterTaskLogV1, "application/json")
