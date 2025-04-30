import json
import os

from flask import current_app
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.models import PersistentIdentifier

from cds_ils.importer.json.importer import JSONImporter
from cds_ils.importer.json.rdm.transform import RDMToILSTransform


def test_rdm_import(app):
    """Test springer record import translation."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "rdm_record.json"), "r") as fp:
        rdm_record = json.load(fp)

    report = JSONImporter("cds").run(rdm_record, mode="IMPORT")

    output_pid = report["output_pid"]

    assert report["action"] == "create"

    document_cls = current_app_ils.document_record_cls
    series_cls = current_app_ils.series_record_cls
    eitem_cls = current_app_ils.eitem_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls

    # setup
    matched_document = document_cls.get_record_by_pid(output_pid)
    assert "alternative_identifiers" in matched_document
    assert matched_document["alternative_identifiers"] == [
        {"value": "aey8d-bdw61", "scheme": "CDS"},
        {"scheme": "INSPIRE", "value": "1393422"},
    ]
    assert matched_document["identifiers"] == [
        {"scheme": "REPORT_NUMBER", "value": "CERN-THESIS-2015-130"},
        {"value": "FERMILAB-THESIS-2015-22", "scheme": "REPORT_NUMBER"},
        {"value": "CMS-TS-2015-021", "scheme": "REPORT_NUMBER"},
        {"value": "CMS-TS-2015-021", "scheme": "REPORT_NUMBER"},
    ]
    assert matched_document["document_type"] == "BOOK"

    series1pid = report["series"][0]["series_record"]["pid"]
    series2pid = report["series"][1]["series_record"]["pid"]
    series1 = series_cls.get_record_by_pid(series1pid)

    assert series1["mode_of_issuance"] == "SERIAL"

    assert matched_document.relations["serial"]
    serial_pids = [x["pid_value"] for x in matched_document.relations["serial"]]
    assert series1pid in serial_pids
    assert series2pid in serial_pids

    eitems = eitem_search_cls().search_by_document_pid(document_pid=output_pid)
    assert eitems.count() == 1
    results = eitems.execute()
    eitem_pid = results.hits[0].pid
    created_eitem = eitem_cls.get_record_by_pid(eitem_pid)

    assert created_eitem["urls"] == [
        {
            "value": "https://127.0.0.1/api/records/aey8d-bdw61/files/CERN-THESIS-2015-130.pdf",
            "description": "e-book",
            "login_required": True,
        }
    ]


def test_rdm_record_update(app, importer_test_data):
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "rdm_record.json"), "r") as fp:
        rdm_record = json.load(fp)

    rdm_record["id"] = "bs29k-ghp04"
    rdm_record["parent"]["id"] = "bs29k-ghp04"

    report = JSONImporter("cds").run(rdm_record, mode="IMPORT")

    output_pid = report["output_pid"]

    assert report["action"] == "update"
    assert output_pid == "docid-2"
    assert report["series"][0]["action"] == "update"
    assert report["series"][1]["action"] == "update"
    assert report["eitem"]["action"] == "update"

    rdm_pid_type = current_app.config["CDS_ILS_RECORD_CDS_RDM_PID_TYPE"]

    rdm_pid = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value == rdm_record["id"],
        PersistentIdentifier.pid_type == rdm_pid_type,
    ).one_or_none()

    assert rdm_pid
    assert rdm_pid.pid_value == rdm_record["id"]


def test_rdm_record_update_legacy_record(app, importer_test_data):
    """Check if we still can find records by legacy recid."""
    document_cls = current_app_ils.document_record_cls

    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "rdm_record.json"), "r") as fp:
        rdm_record = json.load(fp)

    rdm_record["id"] = "stgbc-hzj95"
    rdm_record["parent"]["id"] = "stgbc-hzj95"

    report = JSONImporter("cds").run(rdm_record, mode="IMPORT")

    output_pid = report["output_pid"]

    updated_doc = document_cls.get_record_by_pid(output_pid)
    assert "_rdm_pid" in updated_doc

    assert report["action"] == "update"
    assert output_pid == "docid-3"
    rdm_pid_type = current_app.config["CDS_ILS_RECORD_CDS_RDM_PID_TYPE"]

    rdm_pid = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value == rdm_record["id"],
        PersistentIdentifier.pid_type == rdm_pid_type,
    ).one_or_none()

    assert rdm_pid
    assert rdm_pid.pid_value == rdm_record["id"]
