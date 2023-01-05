import pytest
from invenio_app_ils.proxies import current_app_ils
from invenio_pidstore.errors import PIDDeletedError
from invenio_search import current_search

from cds_ils.importer.eitems.importer import EItemImporter


def test_replace_lower_priority(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls
    eitem_search_cls = current_app_ils.eitem_search_cls

    # setup
    matched_document = document_cls.get_record_by_pid("docid-6")
    current_import_eitem = {
        "urls": [
            {
                "description": "Protected URL",
                "value": "http://protected-cds-ils.ch/",
                "login_required": True,
            },
            {
                "description": "Another open URL",
                "value": "http://cds-ils.ch/",
                "login_required": True,
            },
        ]
    }
    metadata_provider = "springer"
    IS_PROVIDER_PRIORITY_SENSITIVE = True
    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True

    eitem_importer_preview = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )

    eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )

    preview_summary = eitem_importer_preview.preview_import(matched_document)

    # make sure ebl item exists
    eitem_cls.get_record_by_pid("eitemid-6")
    eitem_importer.update_eitems(matched_document)
    summary = eitem_importer.summary()

    current_search.flush_and_refresh(index="*")
    assert len(summary["deleted_eitems"]) == 1
    # check if replaced in the import summary
    assert summary["deleted_eitems"][0]["pid"] == "eitemid-6"
    assert summary["eitem"]["document_pid"] == "docid-6"
    # check if deleted
    with pytest.raises(PIDDeletedError):
        eitem_cls.get_record_by_pid("eitemid-6")
    # check if deleted from the index
    search = eitem_search_cls().search_by_document_pid("docid-6")
    assert search.count() == 0

    # check if preview equals report
    # this should be the only differing item
    summary["output_pid"] = "preview-doc-pid"
    assert preview_summary == summary


def test_import_equal_priority(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls

    # setup
    matched_document = document_cls.get_record_by_pid("docid-6A")
    current_import_eitem = {
        "urls": [
            {
                "description": "Protected URL",
                "value": "http://protected-cds-ils.ch/",
                "login_required": True,
            },
            {
                "description": "Another open URL",
                "value": "http://cds-ils.ch/",
                "login_required": True,
            },
        ]
    }
    metadata_provider = "ebl"
    IS_PROVIDER_PRIORITY_SENSITIVE = False
    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True

    eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )
    preview_eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )

    preview_summary = preview_eitem_importer.preview_import(matched_document)

    eitem_importer.update_eitems(matched_document)
    summary = eitem_importer.summary()
    assert len(summary["deleted_eitems"]) == 0
    # check if replaced in the import summary
    assert summary["eitem"]["document_pid"] == "docid-6A"
    # check if safari not deleted
    eitem_cls.get_record_by_pid("eitemid-6A")
    # check if new record added
    eitem_cls.get_record_by_pid(summary["eitem"]["pid"])

    # check if preview equals report
    summary["output_pid"] = "preview-doc-pid"
    assert preview_summary == summary


def test_do_not_import_lower_priority(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls

    # setup
    matched_document = document_cls.get_record_by_pid("docid-7")
    current_import_eitem = {
        "urls": [
            {
                "description": "Protected URL",
                "value": "http://protected-cds-ils.ch/",
                "login_required": True,
            },
            {
                "description": "Another open URL",
                "value": "http://cds-ils.ch/",
                "login_required": True,
            },
        ]
    }
    metadata_provider = "ebl"
    IS_PROVIDER_PRIORITY_SENSITIVE = False
    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True

    eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )
    preview_eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )

    preview_summary = preview_eitem_importer.preview_import(matched_document)

    eitem_importer.update_eitems(matched_document)
    current_search.flush_and_refresh(index="*")
    summary = eitem_importer.summary()
    assert len(summary["deleted_eitems"]) == 0
    # check if doing nothing
    assert summary["eitem"] is None
    assert summary["action"] == "none"
    # check if higher priority record not deleted
    eitem_cls.get_record_by_pid("eitemid-7")

    # check if preview equals report
    summary["output_pid"] = "preview-doc-pid"
    assert preview_summary == summary


def test_ignore_if_existing_item_not_imported(importer_test_data):
    document_cls = current_app_ils.document_record_cls
    eitem_cls = current_app_ils.eitem_record_cls

    # setup
    matched_document = document_cls.get_record_by_pid("docid-8")
    current_import_eitem = {
        "urls": [
            {
                "description": "Protected URL",
                "value": "http://protected-cds-ils.ch/",
                "login_required": True,
            },
            {
                "description": "Another open URL",
                "value": "http://cds-ils.ch/",
                "login_required": True,
            },
        ]
    }
    metadata_provider = "springer"
    IS_PROVIDER_PRIORITY_SENSITIVE = False
    EITEM_OPEN_ACCESS = False
    EITEM_URLS_LOGIN_REQUIRED = True

    eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )
    preview_eitem_importer = EItemImporter(
        matched_document,
        current_import_eitem,
        metadata_provider,
        IS_PROVIDER_PRIORITY_SENSITIVE,
        EITEM_OPEN_ACCESS,
        EITEM_URLS_LOGIN_REQUIRED,
    )
    preview_summary = preview_eitem_importer.preview_import(matched_document)

    eitem_importer.update_eitems(matched_document)
    summary = eitem_importer.summary()
    assert len(summary["deleted_eitems"]) == 0
    # check if new eitem assigned to doc
    assert summary["eitem"]["document_pid"] == "docid-8"
    # check if user created eitem not deleted (ignored)
    eitem_cls.get_record_by_pid("eitemid-8")
    # check if new record added
    eitem_cls.get_record_by_pid(summary["eitem"]["pid"])

    # check if preview equals report
    summary["output_pid"] = "preview-doc-pid"
    assert preview_summary == summary
