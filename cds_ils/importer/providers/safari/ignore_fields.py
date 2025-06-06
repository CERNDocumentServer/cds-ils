# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS SAFARI Importer ignore xml fields."""

SAFARI_IGNORE_FIELDS = {
    "005",
    "006",
    "007",
    "008",
    "010__a",
    "010__z",
    "015__2",
    "015__a",
    "0167_2",
    "0167_a",
    "0167_z",
    "016__2",
    "016__a",
    "016__z",
    "019__a",
    "0243_a",
    "0243_d",
    "0243_q",
    "0247_2",
    "0247_a",
    "0248_2",
    "0248_a",
    "024__2",
    "024__a",
    "024__q",
    "027__a",
    "02801a",
    "02801b",
    "02802a",
    "02802b",
    "02842a",
    "028__a",
    "028__b",
    "0290_a",
    "0290_b",
    "0290_c",
    "0290_t",
    "0291_a",
    "0291_b",
    "029__a",
    "029__b",
    "035__a",
    "035__z",
    "036__b",
    "037__a",
    "037__b",
    "037__f",
    "037__n",
    "040__a",
    "040__b",
    "040__c",
    "040__d",
    "040__e",
    "0411_h",
    "041__d",
    "041__h",
    "042__a",
    "043__a",
    "046__2",
    "046__k",
    "049__a",
    "05000b",
    "05004b",
    "05010a",
    "05010b",
    "05014a",
    "05014b",
    "050_4b",
    "050__b",
    "05513a",
    "05513b",
    "055_0a",
    "055_0b",
    "055_8a",
    "055_8b",
    "06014a",
    "060_4a",
    "060_4b",
    "066__c",
    "072_72",
    "072_7a",
    "072_7x",
    "072__2",
    "072__a",
    "072__x",
    "080__a",
    "080__b",
    "082002",
    "082042",
    "08204b",
    "082142",
    "08214a",
    "082_4b",
    "082__2",
    "082__b",
    "084_72",
    "084_7a",
    "084__2",
    "084__a",
    "084__b",
    "090__a",
    "092__a",
    "1000_d",
    "1001_0",
    "1001_1",
    "1001_4",
    "1001_c",
    "1001_d",
    "1001_q",
    "100__1",
    "100__4",
    "100__c",
    "100__d",
    "100__q",
    "1101_a",
    "1101_b",
    "1102_a",
    "1112_a",
    "1112_c",
    "1112_d",
    "1112_n",
    "1300_a",
    "1300_l",
    "130__a",
    "130__l",
    "2100_a",
    "24010a",
    "24010l",
    "240__a",
    "240__k",
    "240__l",
    "245006",
    "24500c",
    "24500h",
    "24504c",
    "245106",
    "24510c",
    "24510h",
    "24510n",
    "24510p",
    "24512c",
    "24513c",
    "24514c",
    "24514h",
    "245__6",
    "245__c",
    "245__h",
    "245__n",
    "245__p",
    "246106",
    "2461_i",
    "246306",
    "246336",
    "2463_6",
    "246__6",
    "246__n",
    "246__p",
    "250__6",
    "256__a",
    "263__a",
    "26431a",
    "26431b",
    "26431c",
    "264_16",
    "264__6",
    "264_4c",
    "300__b",
    "300__c",
    "306__a",
    "336__0",
    "336__2",
    "336__a",
    "336__b",
    "337__0",
    "337__2",
    "337__a",
    "337__b",
    "338__0",
    "338__2",
    "338__a",
    "338__b",
    "344__2",
    "344__a",
    "344__b",
    "344__g",
    "344__h",
    "347__2",
    "347__a",
    "347__b",
    "365__b",
    "380__2",
    "380__a",
    "385__2",
    "385__a",
    "386__2",
    "386__a",
    "386__m",
    "386__n",
    "4901_6",
    "4901_x",
    "490__6",
    "500__5",
    "500__6",
    "500__a",
    "504__a",
    "50500g",
    "50500r",
    "5052_a",
    "505__g",
    "5060_2",
    "5060_5",
    "5060_a",
    "5060_f",
    "5061_5",
    "5061_a",
    "5061_c",
    "5061_e",
    "506__2",
    "506__3",
    "506__5",
    "506__a",
    "506__c",
    "506__e",
    "506__f",
    "5104_a",
    "5104_c",
    "5110_a",
    "511__a",
    "5168_a",
    "516__a",
    "5203_4",
    "5208_c",
    "520__6",
    "520__b",
    "520__c",
    "521__a",
    "524__2",
    "524__a",
    "530__a",
    "533__5",
    "533__a",
    "533__b",
    "533__c",
    "533__d",
    "533__n",
    "534__c",
    "534__p",
    "534__z",
    "538__3",
    "538__5",
    "538__a",
    "538__u",
    "540__5",
    "540__a",
    "542__f",
    "542__g",
    "5450_a",
    "545__a",
    "546__a",
    "550__a",
    "5831_2",
    "5831_5",
    "5831_a",
    "5831_c",
    "5831_h",
    "5831_l",
    "5880#a",  # yes, the hash is not a mistake
    "5880_a",
    "588__a",
    "5881_a",
    "590__a",
    "590__b",
    "60000a",
    "60000v",
    "600070",
    "600072",
    "60007a",
    "60010a",
    "60010d",
    "60010q",
    "60010v",
    "60010x",
    "60014a",
    "600170",
    "600172",
    "60017a",
    "60017d",
    "610201",
    "61020a",
    "61020v",
    "61020x",
    "61024a",
    "610270",
    "610272",
    "61027a",
    "610__0",
    "610__2",
    "610__a",
    "610__b",
    "610__v",
    "610__x",
    "63000a",
    "63000v",
    "63000x",
    "630070",
    "630072",
    "63007a",
    "630__0",
    "630__2",
    "630__a",
    "630__v",
    "630__x",
    "647_70",
    "647_72",
    "647_7a",
    "647_7c",
    "647_7d",
    "647__0",
    "647__2",
    "647__a",
    "647__d",
    "648_72",
    "648_7a",
    "648__2",
    "648__a",
    "650072",
    "650076",
    "65012x",
    "650170",
    "650172",
    "650_0a",
    "650_0v",
    "650_0x",
    "650_0y",
    "650_0z",
    "650_20",
    "650_2x",
    "650_4v",
    "650_4x",
    "650_4y",
    "650_60",
    "650_6a",
    "650_6v",
    "650_6x",
    "650_6y",
    "650_6z",
    "650_70",
    "650_72",
    "650_7x",
    "650_7z",
    "650__0",
    "650__2",
    "650__6",
    "650__a",
    "650__v",
    "650__y",
    "650__z",
    "651_0a",
    "651_0x",
    "651_0y",
    "651_4a",
    "651_6a",
    "651_6x",
    "651_6y",
    "651_70",
    "651_72",
    "651_7a",
    "651_7z",
    "651__0",
    "651__2",
    "651__a",
    "651__x",
    "651__y",
    "651__z",
    "6530_a",
    "653_0a",
    "653__a",
    "65504a",
    "655_0a",
    "655_2a",
    "655_4a",
    "655_70",
    "655_72",
    "655_7a",
    "655__0",
    "655__2",
    "655__a",
    "655__v",
    "70002a",
    "70002i",
    "70002l",
    "70002s",
    "70002t",
    "70012t",
    "7001_0",
    "7001_1",
    "7001_4",
    "7001_6",
    "7001_a",
    "7001_c",
    "7001_d",
    "7001_q",
    "7001_t",
    "700__1",
    "700__4",
    "700__6",
    "700__c",
    "700__d",
    "700__i",
    "700__q",
    "700__t",
    "7101_a",
    "7101_b",
    "7101_e",
    "7102_a",
    "7102_e",
    "710__a",
    "710__b",
    "710__e",
    "720__4",
    "720__a",
    "720__e",
    "7300_a",
    "730__a",
    "7400_a",
    "740__a",
    "758",
    "758__4",
    "758__a",
    "758__i",
    "758__1",
    "76508a",
    "76508b",
    "76508d",
    "76508i",
    "76508t",
    "76508w",
    "76508z",
    "765__a",
    "765__b",
    "765__d",
    "765__i",
    "765__t",
    "765__w",
    "765__z",
    "7730_t",
    "77508a",
    "77508d",
    "77508i",
    "77508t",
    "77508w",
    "77508z",
    "775__a",
    "775__d",
    "775__i",
    "775__t",
    "775__w",
    "775__z",
    "77608a",
    "77608b",
    "77608c",
    "77608d",
    "77608h",
    "77608i",
    "77608k",
    "77608n",
    "77608t",
    "77608w",
    "77608z",
    "7760_z",
    "7761_c",
    "7761_z",
    "776__a",
    "776__b",
    "776__c",
    "776__d",
    "776__i",
    "776__s",
    "776__t",
    "776__w",
    "776__z",
    "78608n",
    "7870_n",
    "8001_a",
    "8001_t",
    "8001_v",
    "830_06",
    "830_0a",
    "830_0p",
    "830_0v",
    "830_0x",
    "830__6",
    "830__a",
    "830__h",
    "830__s",
    "830__v",
    "85640z",
    "880006",
    "88000a",
    "88000b",
    "88000c",
    "88000h",
    "880072",
    "880076",
    "88007a",
    "8800_6",
    "8800_a",
    "8800_t",
    "880106",
    "88010a",
    "88010b",
    "88010c",
    "88010h",
    "8801_6",
    "8801_a",
    "8801_c",
    "8801_d",
    "8801_e",
    "880306",
    "88030a",
    "880336",
    "88033a",
    "8803_6",
    "8803_a",
    "8808_6",
    "8808_a",
    "880_06",
    "880_0a",
    "880_16",
    "880_1a",
    "880_1b",
    "880_1c",
    "880__2",
    "880__6",
    "880__a",
    "880__b",
    "880__c",
    "880__d",
    "880__e",
    "880__t",
    "887__2",
    "887__a",
    "902__g",
    "902__h",
    "938__a",
    "938__b",
    "938__c",
    "938__d",
    "938__i",
    "938__n",
    "938__s",
    "949__x",
    "994__a",
    "994__b",
}
