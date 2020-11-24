import pytest

from cds_ils.importer.errors import MissingRequiredField
from cds_ils.importer.providers.cds.rules.utils import extract_volume_info, \
    extract_volume_number

volume_params = [
    ("v1", "1", False),
    ("v 1", "1", False),
    ("v.1", "1", False),
    ("v. 1", "1", False),
    ("v . 1", "1", False),
    ("vol.1", "1", False),
    ("Vol. 2", "2", False),
    ("voL . 1", None, False),
    ("volume.1", "1", False),
    ("Volume. 1", "1", False),
    ("volume . 3", "3", False),
    ("pt 5", "5", False),
    ("part 5", "5", False),
    ("par 5", None, False),
    ("v. A", "A", False),
    ("val. 5", None, False),
    ("part III", "III", False),
    ("March 1996", None, False),
]


@pytest.mark.parametrize("value, expected, raise_exception", volume_params)
def test_extract_volume_number(value, expected, raise_exception):
    """Test extracting volume number."""
    if raise_exception:
        with pytest.raises(MissingRequiredField):
            assert (
                extract_volume_number(value, raise_exception=raise_exception)
                == expected
            )
    else:
        assert extract_volume_number(value) == expected


volume_info_params = [
    (
        "print version, paperback ({})".format(vol_str),
        dict(volume=expected, description="print version, paperback")
        if expected
        else None,
    )
    for vol_str, expected, raise_exception in volume_params
]
volume_info_params.append(("print version, paperback v.5", None))


@pytest.mark.parametrize("value, expected", volume_info_params)
def test_extract_volume_info(value, expected):
    """Test extracting volume info."""
    assert extract_volume_info(value) == expected
