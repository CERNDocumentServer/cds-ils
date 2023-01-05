# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS EItems helpers."""


def clean_url_provider(
    url_value,
    url_description,
    record_dict,
):
    """Clean eitem provider url object for migration.

    :param url_value: URI of eitem
    :param url_description: Label of the url
    :param record_dict dictionary of eitem's parent record
    (document or multipart)
    :param migration_dict support dictionary for migration
    """

    def translate_open_access(item, open_access_field):
        if open_access_field:
            is_open_access = "open access" in open_access_field.lower()
            item["open_access"] = is_open_access

    eitems_ebl = record_dict["_migration"]["eitems_ebl"]
    eitems_safari = record_dict["_migration"]["eitems_safari"]
    eitems_external = record_dict["_migration"]["eitems_external"]
    eitems_proxy = record_dict["_migration"]["eitems_proxy"]
    eitems_files = record_dict["_migration"]["eitems_file_links"]

    eitem_dict = {"url": {"value": url_value}}
    if url_description:
        eitem_dict["url"]["description"] = url_description

    # EBL publisher login required
    # No need to check for open_access since EBL is always restricted
    if all([elem in url_value for elem in ["cds", ".cern.ch" "/auth.py"]]):
        eitems_ebl.append(eitem_dict)
        record_dict["_migration"]["eitems_has_ebl"] = True
    # EzProxy links
    elif "ezproxy.cern.ch" in url_value:
        translate_open_access(eitem_dict, url_description)
        eitem_dict["url"]["value"] = eitem_dict["url"]["value"].replace(
            "https://ezproxy.cern.ch/login?url=", ""
        )
        eitems_proxy.append(eitem_dict)
        record_dict["_migration"]["eitems_has_proxy"] = True
    # Safari links
    # No need to check for open_access since Safari is always restricted
    elif url_value.startswith("https://learning.oreilly.com/library/view/"):
        eitems_safari.append(eitem_dict)
        record_dict["_migration"]["eitems_has_safari"] = True
    # local files
    # No need to check for open_access since for local files open_access is
    # controlled by files restriction itself
    elif all([elem in url_value for elem in ["cds", ".cern.ch/record/", "/files"]]):
        eitems_files.append(eitem_dict)
        record_dict["_migration"]["eitems_has_files"] = True
    elif url_description in ["ebook", "e-book", "e-proceedings"]:
        translate_open_access(eitem_dict, url_description)
        eitems_external.append(eitem_dict)
        record_dict["_migration"]["eitems_has_external"] = True
    else:
        # if none of the above, it is just external url
        # attached to the document
        return eitem_dict["url"]
