"""Book model."""
from __future__ import unicode_literals

from copy import deepcopy

from cds_dojson.overdo import OverdoJSONSchema

from ..cds import get_helper_dict
from ..cds import model as base_model
from ..ignore_fields import CDS_IGNORE_FIELDS


class CDSBook(OverdoJSONSchema):
    """Translation Index for CDS Books."""

    __query__ = (
        '690C_:BOOK OR 690C_:"YELLOW REPORT" OR '
        "980__:PROCEEDINGS OR 980__:PERI OR "
        "(-980:STANDARD 980:BOOK) OR "
        "697C_:LEGSERLIB "
        "-980__:DELETED -980__:MIGRATED -980:__STANDARD -596:MULTIVOLUMES"
    )

    __model_ignore_keys__ = {
        "020__b",  # this field is used to match multipart monograph items as volumes
    }

    __ignore_keys__ = CDS_IGNORE_FIELDS | __model_ignore_keys__

    _default = {"_migration": {**get_helper_dict()}}


model = CDSBook(
    bases=(base_model,), entry_point_group="cds_ils.importer.cds.document"
)
