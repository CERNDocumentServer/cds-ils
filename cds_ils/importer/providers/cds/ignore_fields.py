# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer ignored fields."""

CDS_IGNORE_FIELDS = {
    "003",
    "005",
    "020__q",
    "020__c",
    "020__b",  # this field is used to match multipart items as volumes
    "020__C",
    "0248_a",
    "0248_p",
    "041__h",  # 206 cds-dojson
    "035__z",
    "037__c",  # arXiv subject category
    "050__b",
    "050_4b",
    "082002",
    "082042",
    "0820_2",
    "082__2",  # INSPIRE keywords
    "084__a",  # INSPIRE keywords
    "084__2",
    "100__9",
    "111__d",
    "111__f",
    "145__a",
    "246__i",
    "269__a",  # preprint info
    "269__b",  # preprint info
    "269__c",  # preprint date
    "270__m",  # conference email
    "300__b",  # 206 cds-dojson
    "340__a",
    "440_3a",  # 206 cds-dojson
    "541__9",
    "541__a",
    "541__h",
    "502__a",  # thesis_info/defense_date
    "502__b",  # thesis_info/degree_type
    "502__c",  # thesis_info/institutions
    "502__d",  # thesis_info/date (publication)
    "5208_a",  # 206 cds-dojson
    "520__9",
    "536__a",  # founding info, dropped
    "536__c",
    "536__f",
    "540__b",
    "540__f",
    "595__z",
    "595__9",
    "596__a",
    "597__a",
    "650172",
    "65017a",
    "650272",
    "65027a",
    "690__c",  # 206 cds-dojson
    "694__9",
    "694__a",
    "695__2",
    "695__a",
    "700__9",
    "710__5",
    "773__r",  # publication_info/parent_report_number
    "773__w",  # inspire cnum (duplicated field with 035__9)
    "773__z",  # publication_info/parent_isbn
    "775__c",  # related edition's year (it will be resolved)
    "852__c",
    "852__h",
    "852__p",
    "8564_8",  # bibdoc id
    "8564_s",  # file identifier
    "8564_x",  # subformat identifier
    "900__s",  # 206 cds-dojson
    "900__u",  # 206 cds-dojson
    "900__y",  # 206 cds-dojson
    "901__a",  # record affiliation
    "901__u",
    "916__a",
    "916__d",
    "916__e",
    "916__y",
    "940__u",
    "961__c",
    "961__h",
    "961__l",
    "961__x",
    "962__b",
    "962__n",  # books connected by conference
    "963__a",
    "964__a",
    "970__a",
    "970__d",
    "980__c",
    "981__a",
}
