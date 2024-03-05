import random

from cds_ils.importer.series.importer import SeriesImporter

from ..helpers import load_json_from_datadir


def test_series_search_matching(importer_test_data):
    def match(json_series):
        matching_series_pids = series_importer.search_for_matching_series(json_series)
        # sort randomly to ensure tests are not based on order
        random.shuffle(matching_series_pids)
        return series_importer._validate_matches(json_series, matching_series_pids)

    metadata_provider = "springer"

    series_to_import = load_json_from_datadir(
        "match_testing_series.json", relpath="importer"
    )

    series_importer = SeriesImporter(
        series_to_import,
        metadata_provider,
    )

    # test matching by exact title
    json_series = series_to_import[0]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-1"

    # test matching by normalized title
    json_series = series_to_import[1]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-1"

    # test not matching by normalized title
    json_series = series_to_import[2]
    validated_matches = match(json_series)
    assert len(validated_matches) == 0

    # test matching by ISSN
    json_series = series_to_import[3]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-2"

    # test matching by ISSN and publisher
    json_series = series_to_import[4]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-3"

    # test matching by ISSN, year and publisher
    json_series = series_to_import[5]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-4"

    # test wrong `mode_of_issuance`
    json_series = series_to_import[6]
    validated_matches = match(json_series)
    assert len(validated_matches) == 0

    # test wrong `series_type`
    json_series = series_to_import[7]
    validated_matches = match(json_series)
    assert len(validated_matches) == 0

    # test different year
    json_series = series_to_import[8]
    validated_matches = match(json_series)
    assert len(validated_matches) == 0

    # test different publisher
    json_series = series_to_import[9]
    validated_matches = match(json_series)
    assert len(validated_matches) == 0

    # test duplicated title
    json_series = series_to_import[10]
    validated_matches = match(json_series)
    assert len(validated_matches) == 2

    # test whitespace title
    json_series = series_to_import[11]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-1"

    # test `ser` suffix and different capitalization in title
    json_series = series_to_import[12]
    validated_matches = match(json_series)
    assert len(validated_matches) == 1
    assert validated_matches[0] == "serid-imp-1"
