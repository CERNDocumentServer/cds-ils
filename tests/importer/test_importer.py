import time

from invenio_app_ils.proxies import current_app_ils
from invenio_search import current_search

from cds_ils.importer.importer import Importer
from tests.helpers import load_json_from_datadir


def test_modify_documents(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir("modify_document_data.json", relpath="importer")

    importer = Importer(json_data[0], "springer")
    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "update"

    updated_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    # wait for indexing
    current_search.flush_and_refresh(index="*")

    search = eitem_search_cls().search_by_document_pid(
        document_pid=updated_document["pid"]
    )
    results = search.execute()

    assert results.hits.total.value == 1

    eitem_pid = results.hits[0].pid
    updated_eitem = eitem_cls.get_record_by_pid(eitem_pid)

    # check if new identifier added
    assert updated_document["identifiers"] == [
        {"scheme": "DOI", "value": "0123456789"},
        {"scheme": "ISBN", "value": "0987654321"},
    ]

    assert updated_eitem["description"] == "Modified description"


def test_import_audiobook_with_existing_ebook(importer_test_data):
    # Test to check that a new eitem is created when there is an existing eitem but of different eitem_type
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls

    # Import an audiobook for a document with an existing ebook
    json_data = load_json_from_datadir(
        "documents_with_audiobook.json", relpath="importer"
    )
    importer = Importer(json_data[0], "safari")

    report = importer.import_record()
    assert report["action"] == "update"
    assert report["eitem"]["action"] == "create"

    updated_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    time.sleep(1)
    search = eitem_search_cls().search_by_document_pid(
        document_pid=updated_document["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 2

    created_eitem_pid = results.hits[1].pid
    eitem = eitem_cls.get_record_by_pid(created_eitem_pid)

    assert eitem["document_pid"] == updated_document["pid"]
    assert eitem["eitem_type"] == "AUDIOBOOK"

    assert "_eitem" not in updated_document
    assert "agency_code" not in updated_document
    assert "identifiers" in updated_document

    for isbn in updated_document["identifiers"]:
        assert isbn["material"] == "AUDIOBOOK"

    assert eitem["created_by"] == {"type": "import", "value": "safari"}


def test_import_update_existing_audiobook(importer_test_data):
    # Test to check that the existing audiobook is updated having same provider
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls

    # Import an audiobook for a document with an existing audiobook
    json_data = load_json_from_datadir(
        "documents_with_audiobook.json", relpath="importer"
    )
    importer = Importer(json_data[1], "safari")

    report = importer.import_record()
    assert report["action"] == "update"
    assert report["eitem"]["action"] == "update"

    updated_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    time.sleep(1)
    search = (
        eitem_search_cls()
        .search_by_document_pid(document_pid=updated_document["pid"])
        .filter("term", eitem_type="AUDIOBOOK")
    )
    results = search.execute()
    assert results.hits.total.value == 1

    updated_eitem_pid = results.hits[0].pid
    eitem = eitem_cls.get_record_by_pid(updated_eitem_pid)

    assert eitem["document_pid"] == updated_document["pid"]
    assert eitem["eitem_type"] == "AUDIOBOOK"

    assert "_eitem" not in updated_document
    assert "agency_code" not in updated_document
    assert "identifiers" in updated_document

    for isbn in updated_document["identifiers"]:
        assert isbn["material"] == "AUDIOBOOK"

    assert eitem["created_by"] == {"type": "import", "value": "safari"}


def test_import_documents(app, db):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir("create_documents_data.json", relpath="importer")
    importer = Importer(json_data[0], "springer")
    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "create"

    document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    time.sleep(1)
    search = eitem_search_cls().search_by_document_pid(document_pid=document["pid"])
    results = search.execute()
    assert results.hits.total.value == 1

    eitem_pid = results.hits[0].pid
    eitem = eitem_cls.get_record_by_pid(eitem_pid)

    assert eitem["document_pid"] == document["pid"]
    assert eitem["eitem_type"] == "E-BOOK"

    assert "_eitem" not in document
    assert "agency_code" not in document

    for urls in eitem["urls"]:
        urls["description"] == "e-book"

    assert eitem["created_by"] == {"type": "import", "value": "springer"}
    assert document["created_by"] == {"type": "import", "value": "springer"}


def test_replace_eitems_by_provider_priority(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir("modify_document_data.json", relpath="importer")

    document_before_update = document_cls.get_record_by_pid("docid-1")
    search = eitem_search_cls().search_by_document_pid(
        document_pid=document_before_update["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 1
    eitem_before_update = eitem_cls.get_record_by_pid(results.hits[0].pid)
    assert eitem_before_update["created_by"] == {
        "type": "import",
        "value": "ebl",
    }

    ProviderImporter = Importer
    ProviderImporter.IS_PROVIDER_PRIORITY_SENSITIVE = True
    importer = ProviderImporter(json_data[1], "springer")
    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "update"
    assert report["eitem"]["action"] == "replace"

    updated_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    # wait for indexing
    time.sleep(1)

    search = eitem_search_cls().search_by_document_pid(
        document_pid=updated_document["pid"]
    )
    results = search.execute()

    # check if previous eitems deleted, and added only one from this provider
    assert results.hits.total.value == 1
    eitem_pid = results.hits[0].pid
    updated_eitem = eitem_cls.get_record_by_pid(eitem_pid)
    assert updated_eitem["created_by"] == {
        "type": "import",
        "value": "springer",
    }
    assert updated_eitem["description"] == "E-BOOK TO OVERWRITE"


def test_add_eitems_by_type(importer_test_data):
    # Test to check that a new eitem is created when there is an existing eitem but with different eitem_type and different provider
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir("modify_document_data.json", relpath="importer")

    document_before_update = document_cls.get_record_by_pid(json_data[2]["pid"])
    search = eitem_search_cls().search_by_document_pid(
        document_pid=document_before_update["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 1

    ProviderImporter = Importer
    ProviderImporter.IS_PROVIDER_PRIORITY_SENSITIVE = True
    importer = ProviderImporter(json_data[2], "safari")
    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "update"
    assert report["eitem"]["action"] == "create"

    updated_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    # wait for indexing
    time.sleep(1)

    search = eitem_search_cls().search_by_document_pid(
        document_pid=updated_document["pid"]
    )
    results = search.execute()

    # check if previous E-BOOK persisted, and added only AUDIOBOOK from this provider
    assert results.hits.total.value == 2
    ebook_pid = results.hits[0].pid
    audiobook_pid = results.hits[1].pid
    ebook = eitem_cls.get_record_by_pid(ebook_pid)
    audiobook = eitem_cls.get_record_by_pid(audiobook_pid)
    assert ebook["created_by"] == {
        "type": "import",
        "value": "springer",
    }
    assert audiobook["created_by"] == {
        "type": "import",
        "value": "safari",
    }
    assert audiobook["description"] == "AUDIOBOOK TO ADD"


def test_add_document_to_serial(app, db):
    document_cls = current_app_ils.document_record_cls
    series_cls = current_app_ils.series_record_cls

    json_data = load_json_from_datadir(
        "new_document_with_serial.json", relpath="importer"
    )

    importer = Importer(json_data[0], "springer")

    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "create"
    assert report["series"]

    created_document = document_cls.get_record_by_pid(report["document_json"]["pid"])

    series_list = []
    for series in report["series"]:
        series_list.append(series_cls.get_record_by_pid(series["series_record"]["pid"]))

    assert series_list[0]["title"] == "Advances in Nuclear Physics ;"
    assert series_list[0]["identifiers"] == [{"scheme": "ISSN", "value": "123455"}]
    # check if relations creates
    assert (
        created_document["relations_extra_metadata"]["serial"][0]["pid_value"]
        == series_list[0]["pid"]
    )
    assert created_document["relations_extra_metadata"]["serial"][0]["volume"] == "26"


def test_import_audiobook(app, db):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir(
        "documents_with_audiobook.json", relpath="importer"
    )
    importer = Importer(json_data[0], "safari")

    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "create"

    created_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    time.sleep(1)
    search = eitem_search_cls().search_by_document_pid(
        document_pid=created_document["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 1

    eitem_pid = results.hits[0].pid
    eitem = eitem_cls.get_record_by_pid(eitem_pid)

    assert eitem["document_pid"] == created_document["pid"]
    assert eitem["eitem_type"] == "AUDIOBOOK"

    assert "_eitem" not in created_document
    assert "agency_code" not in created_document
    assert "identifiers" in created_document

    for urls in eitem["urls"]:
        urls["description"] == "audiobook"

    for isbn in created_document["identifiers"]:
        assert isbn["material"] == "AUDIOBOOK"

    assert eitem["created_by"] == {"type": "import", "value": "safari"}
    assert created_document["created_by"] == {"type": "import", "value": "safari"}


def test_import_video(app, db):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir("documents_with_video.json", relpath="importer")
    importer = Importer(json_data[0], "safari")

    report = importer.import_record()
    assert report["document_json"]
    assert report["action"] == "create"

    created_document = document_cls.get_record_by_pid(report["document_json"]["pid"])
    assert created_document["document_type"] == "MULTIMEDIA"
    time.sleep(1)
    search = eitem_search_cls().search_by_document_pid(
        document_pid=created_document["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 1

    eitem_pid = results.hits[0].pid
    eitem = eitem_cls.get_record_by_pid(eitem_pid)

    assert eitem["document_pid"] == created_document["pid"]
    assert eitem["eitem_type"] == "VIDEO"

    assert "_eitem" not in created_document
    assert "agency_code" not in created_document
    assert "identifiers" in created_document

    for urls in eitem["urls"]:
        urls["description"] == "video"

    for isbn in created_document["identifiers"]:
        assert isbn["material"] == "VIDEO"

    assert eitem["created_by"] == {"type": "import", "value": "safari"}
    assert created_document["created_by"] == {"type": "import", "value": "safari"}
