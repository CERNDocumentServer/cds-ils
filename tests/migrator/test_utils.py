import pytest

from cds_ils.importer.errors import MissingRequiredField
from cds_ils.importer.providers.cds.helpers.parsers import (
    extract_volume_info,
    extract_volume_number,
)

volume_params = [
    ("v1", "v1", False),
    ("v 1", "v 1", False),
    ("v.1", "1", False),
    ("v. 1", "1", False),
    ("v . 1", "1", False),
    ("vol.1", "vol.1", False),
    ("Vol. 2", "Vol. 2", False),
    ("voL . 1", "voL . 1", False),
    ("volume.1", "volume.1", False),
    ("Volume. 1", "Volume. 1", False),
    ("volume . 3", "volume . 3", False),
    ("pt 5", "pt 5", False),
    ("part 5", "part 5", False),
    ("par 5", "par 5", False),
    ("v. A", "A", False),
    ("val. 5", "val. 5", False),
    ("part III", "part III", False),
    ("March 1996", "March 1996", False),
]


@pytest.mark.parametrize("value, expected, raise_exception", volume_params)
def test_extract_volume_number(value, expected, raise_exception):
    """Test extracting volume number."""
    if raise_exception:
        with pytest.raises(MissingRequiredField):
            assert extract_volume_number(value) == expected
    else:
        assert extract_volume_number(value) == expected


volume_info_params = [
    (
        "print version, paperback ({})".format(vol_str),
        (
            dict(volume=expected, description="print version, paperback")
            if expected
            else None
        ),
    )
    for vol_str, expected, raise_exception in volume_params
]
volume_info_params.append(("print version, paperback v.5", None))


@pytest.mark.parametrize("value, expected", volume_info_params)
def test_extract_volume_info(value, expected):
    """Test extracting volume info."""
    assert extract_volume_info(value) == expected
