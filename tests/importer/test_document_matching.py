from cds_ils.importer.documents.api import fuzzy_search_document
from cds_ils.importer.documents.importer import DocumentImporter

from ..helpers import load_json_from_datadir


def test_document_search_matching(importer_test_data):
    helper_metadata_fields = ("_items", "agency_code")
    metadata_provider = "springer"
    update_document_fields = ("identifiers", "alternative_identifiers")

    data_to_update = load_json_from_datadir(
        "match_testing_documents.json", relpath="importer"
    )

    # test matching by ISBN
    document_importer = DocumentImporter(
        data_to_update[0],
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    )

    matches = document_importer.search_for_matching_documents()
    validated_matches, partial = document_importer.validate_found_matches(matches)

    assert validated_matches == "docid-1"

    # test matching by DOI
    document_importer = DocumentImporter(
        data_to_update[1],
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    )

    matches = document_importer.search_for_matching_documents()
    validated_matches, partial = document_importer.validate_found_matches(matches)

    assert validated_matches == "docid-3"

    # test matching by title and author
    document_importer = DocumentImporter(
        data_to_update[2],
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    )

    matches = document_importer.search_for_matching_documents()
    validated_matches, partial = document_importer.validate_found_matches(matches)

    assert validated_matches == "docid-4"

    # test matching by title and authors but different ids
    document_importer = DocumentImporter(
        data_to_update[4],
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    )

    matches = document_importer.search_for_matching_documents()
    validated_matches, partial = document_importer.validate_found_matches(matches)

    assert validated_matches == "docid-4"
    assert partial == ["docid-41"]

    # test matching by normalized title and author
    document_importer = DocumentImporter(
        data_to_update[5],
        helper_metadata_fields,
        metadata_provider,
        update_document_fields,
    )

    matches = document_importer.search_for_matching_documents()
    validated_matches, partial = document_importer.validate_found_matches(matches)

    assert validated_matches == "docid-4"
    assert partial == ["docid-41"]


def test_fuzzy_matching(importer_test_data):
    data_to_update = load_json_from_datadir(
        "match_testing_documents.json", relpath="importer"
    )[3]

    authors = [author["full_name"] for author in data_to_update.get("authors", [])]

    results = fuzzy_search_document(data_to_update["title"], authors).scan()
    matches = [x.pid for x in results]
    assert matches == ["docid-5"]
