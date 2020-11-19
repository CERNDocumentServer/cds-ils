from __future__ import unicode_literals

from copy import deepcopy

from cds_dojson.overdo import OverdoJSONSchema

from ..cds import get_helper_dict
from ..cds import model as base_model
from ..ignore_fields import CDS_IGNORE_FIELDS


class CDSStandard(OverdoJSONSchema):
    """Translation Index for CDS Books."""

    __query__ = (
        "690C_:STANDARD OR 980__:STANDARD -980__:DELETED -980__:MIGRATED"
    )

    __ignore_keys__ = CDS_IGNORE_FIELDS

    _default = {"_migration": {**get_helper_dict()}}


model = CDSStandard(
    bases=(base_model,), entry_point_group="cds_dojson.importer.document"
)
