from copy import deepcopy

import pytest
from invenio_app_ils.errors import VocabularyError

from cds_ils.importer.vocabularies_validator import Validator

VOCABULARIES_FIELDS = {
    "field1": {
        "source": "json",
        "type": "field1_keys",
    },
    "field2_obj": {
        "subfield2": {
            "source": "json",
            "type": "subfield2_keys",
        },
    },
    "field3_list": {
        "subfield3": {
            "source": "json",
            "type": "subfield3_keys",
        }
    },
    "field4": {
        "source": "elasticsearch",
        "type": "license",
    },
    "field5_simple_list": {
        "source": "json",
        "type": "field5_keys",
    },
}

RECORD = {
    "not_a_vocab": "a value",
    "field1": "FIELD1_VALID_KEY",
    "field2_obj": {
        "subfield2": "SUBFIELD2_VALID_KEY",
    },
    "field3_list": [
        {
            "subfield3": "SUBFIELD3_VALID_KEY_1",
        },
        {
            "subfield3": "SUBFIELD3_VALID_KEY_2",
        },
    ],
    "field4": "FIELD4_VALID_KEY",
    "field5": [
        "FIELD5_VALID_KEY_1",
        "FIELD5_VALID_KEY_2",
        "FIELD5_VALID_KEY_3",
    ],
}


def test_validator(mocker):
    """Vocabulary validator tests."""

    def _raise(ex):
        """Raise exception, needed for lambdas."""
        raise ex

    validator = Validator()

    def test_all_valid():
        """Test that will not raise when all values are valid."""
        # return the same keys as the one validated to fake that the
        # vocabularies contain such values
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.json_fetcher",
            side_effect=lambda vocab_type, key: [key],
        )
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.es_fetcher",
            side_effect=lambda vocab_type, key: key,
        )
        # no exception raised
        validator.validate(VOCABULARIES_FIELDS, RECORD)

    def test_wrong_vocab_source():
        """Test that will raise when source is invalid."""
        definitions = deepcopy(VOCABULARIES_FIELDS)
        definitions["field1"] = {
            "source": "wrong",
            "type": "field1_keys",
        }
        with pytest.raises(VocabularyError):
            validator.validate(definitions, RECORD)

    def test_wrong_vocab_type():
        """Test that will raise when type is invalid."""
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.json_fetcher",
            side_effect=lambda vocab_type, key: _raise(KeyError),
        )
        with pytest.raises(KeyError):
            validator.validate(VOCABULARIES_FIELDS, RECORD)

    def test_wrong_vocab_file():
        """Test that will raise when source file does not exist."""
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.json_fetcher",
            side_effect=lambda vocab_type, key: _raise(FileNotFoundError),
        )
        with pytest.raises(FileNotFoundError):
            validator.validate(VOCABULARIES_FIELDS, RECORD)

    def test_field2_obj_key_missing_json():
        """Test that will raise when vocab key doesn't exist in JSON source."""
        # key not found in JSON files
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.json_fetcher",
            side_effect=lambda vocab_type, key: [],
        )
        with pytest.raises(VocabularyError):
            validator.validate(VOCABULARIES_FIELDS, RECORD)

    def test_field2_obj_key_missing_es():
        """Test that will raise when vocab key doesn't exist in ES source."""
        # key not found in ES
        mocker.patch(
            "cds_ils.importer.vocabularies_validator.es_fetcher",
            side_effect=lambda vocab_type, key: None,
        )
        with pytest.raises(VocabularyError):
            validator.validate(VOCABULARIES_FIELDS, RECORD)

    tests = [
        test_all_valid,
        test_wrong_vocab_source,
        test_wrong_vocab_type,
        test_wrong_vocab_file,
        test_field2_obj_key_missing_json,
        test_field2_obj_key_missing_es,
    ]

    for test in tests:
        test()
        validator.reset()
        mocker.resetall()
