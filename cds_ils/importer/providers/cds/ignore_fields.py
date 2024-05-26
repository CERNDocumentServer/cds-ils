# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS CDS Importer ignored fields."""
CDS_IGNORE_FIELDS = {
    "003",
    "003___",
    "005",
    "020__q",
    "020__c",
    "020__b",  # this field is used to match multipart items as volumes
    "020__C",
    "0248_a",
    "0248_p",
    "0248_q",
    "0247_9",
    "041__h",  # 206 cds-dojson
    "035__d",
    "035__h",
    "035__m",
    "035__t",
    "035__u",
    "035__z",
    "037__c",  # arXiv subject category
    "050__b",
    "050_4b",
    "050_0b",
    "05000b",
    "05010b",
    "05014b",
    "08204b",
    "082002",
    "082042",
    "0820_2",
    "082__2",  # INSPIRE keywords
    "084__a",  # INSPIRE keywords
    "084__2",
    "084__b",
    "100__1",
    "100__4",
    "100__d",
    "100__v",
    "100__9",
    "100__i",
    "111__d",
    "111__f",
    "111__y",
    "145__a",
    "245__9",
    "246__9",
    "246__i",
    "269__a",  # preprint info
    "269__b",  # preprint info
    "269__c",  # preprint date
    "270__a",
    "270__d",
    "270__k",
    "270__l",
    "270__m",  # conference email
    "300__b",  # 206 cds-dojson
    "440_3a",  # 206 cds-dojson
    "541__9",
    "541__a",
    "541__h",
    "500__9",
    "502__a",  # thesis_info/defense_date
    "502__b",  # thesis_info/degree_type
    "502__c",  # thesis_info/institutions
    "502__d",  # thesis_info/date (publication)
    "5208_a",  # 206 cds-dojson
    "50500g",
    "520__c",
    "520__9",
    "536__a",  # founding info, dropped
    "536__c",
    "536__f",
    "540__b",
    "540__f",
    "562__c",
    "595__z",
    "595__9",
    "596__a",
    "597__a",
    "65017b",
    "650172",
    "65017a",
    "650272",
    "65027a",
    "65027b",
    "690__c",  # 206 cds-dojson
    "693__s",
    "694__9",
    "694__a",
    "695__2",
    "695__9",
    "695__a",
    "700__1",
    "700__9",
    "700__d",
    "700__m",
    "700__v",
    "700__i",
    "710__5",
    "711__d",
    "711__f",
    "758__4",
    "758__a",
    "758__i",
    "758__1",
    "773__0",  # on library request
    "773__r",  # publication_info/parent_report_number
    "773__w",  # inspire cnum (duplicated field with 035__9)
    "773__z",  # publication_info/parent_isbn
    "775__c",  # related edition's year (it will be resolved)
    "775__p",
    "775__n",
    "7870_i",
    "7870_r",
    "7870_w",
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
    "903__a",
    "903__s",
    "905__a",
    "905__p",
    "912__a",
    "912__n",
    "912__f",
    "912__p",
    "912__r",
    "916__a",
    "916__d",
    "916__e",
    "916__y",
    "940__u",
    "961__c",
    "961__h",
    "961__l",
    "961__x",
    "962__k",
    "962__b",
    "962__n",  # books connected by conference
    "963__a",
    "964__a",
    "970__a",
    "970__d",
    "980__c",
    "981__a",
}
