import time

from invenio_app_ils.proxies import current_app_ils

from cds_ils.importer.importer import Importer
from cds_ils.importer.series.importer import SeriesImporter
from tests.helpers import load_json_from_datadir


def test_modify_documents(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir(
        "modify_document_data.json", relpath="importer"
    )

    importer = Importer(json_data[0], "springer")
    report = importer.import_record()
    assert report["updated"]

    updated_document = document_cls.get_record_by_pid(report["updated"]["pid"])
    # wait for indexing
    time.sleep(1)

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


def test_import_documents(app, db):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir(
        "create_documents_data.json", relpath="importer"
    )
    importer = Importer(json_data[0], "springer")
    report = importer.import_record()
    assert report["created"]

    document = document_cls.get_record_by_pid(report["created"]["pid"])
    time.sleep(1)
    search = eitem_search_cls().search_by_document_pid(
        document_pid=document["pid"]
    )
    results = search.execute()
    assert results.hits.total.value == 1

    eitem_pid = results.hits[0].pid
    eitem = eitem_cls.get_record_by_pid(eitem_pid)

    assert eitem["document_pid"] == document["pid"]

    assert "_eitem" not in document
    assert "agency_code" not in document

    assert eitem["created_by"] == {"type": "import", "value": "springer"}
    assert document["created_by"] == {"type": "import", "value": "springer"}


def test_replace_eitems_by_provider_priority(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls
    eitem_cls = current_app_ils.eitem_record_cls

    json_data = load_json_from_datadir(
        "modify_document_data.json", relpath="importer"
    )

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
    assert report["updated"]

    updated_document = document_cls.get_record_by_pid(report["updated"]["pid"])
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
    assert updated_eitem["description"] == "EITEM TO OVERWRITE"


def test_add_document_to_serial(app, db):
    document_cls = current_app_ils.document_record_cls
    series_cls = current_app_ils.series_record_cls

    json_data = load_json_from_datadir(
        "new_document_with_serial.json", relpath="importer"
    )

    importer = Importer(json_data[0], "springer")

    report = importer.import_record()
    assert report["created"]
    assert report["series"]

    created_document = document_cls.get_record_by_pid(report["created"]["pid"])

    series_list = []
    for series in report["series"]:
        series_list.append(series_cls.get_record_by_pid(series["pid"]))

    assert series_list[0]["title"] == "Advances in Nuclear Physics ;"
    assert series_list[0]["identifiers"] == [
        {"scheme": "ISSN", "value": "123455"}
    ]
    # check if relations creates
    assert (
        created_document["relations_extra_metadata"]["serial"][0]["pid_value"]
        == series_list[0]["pid"]
    )
    assert (
        created_document["relations_extra_metadata"]["serial"][0]["volume"]
        == "26"
    )
