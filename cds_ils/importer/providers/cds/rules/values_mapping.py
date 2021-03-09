# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS MARCXML to JSON fields values mapping."""

from __future__ import unicode_literals

from cds_ils.importer.errors import UnexpectedValue

DOCUMENT_TYPE = {
    "PROCEEDINGS": ["PROCEEDINGS", "42", "43"],
    "BOOK": ["BOOK", "21"],
    "STANDARD": ["STANDARD"],
}

COLLECTION = {
    "BOOK_SUGGESTION": ["BOOKSUGGESTION"],
    "DIDATIC_LIBRARY": ["DIDACTICLIBRARY"],
    "LEGAL_SERVICE_LIBRARY": ["LEGSERLIB"],
    "ARCHIVES": ["PAULISCIENTIFICBOOK"],
    "CERN": ["CERN"],
    "BOOKSHOP": ["BOOKSHOP"],
    "LEGSERLIBINTLAW": ["LEGSERLIBINTLAW"],
    "LEGSERLIBCIVLAW": ["LEGSERLIBCIVLAW"],
    "LEGSERLIBLEGRES": ["LEGSERLIBLEGRES"],
}

SERIAL = {
    "DESIGN REPORT": ["DESIGN REPORT", "DESIGNREPORT"],
}

ACQUISITION_METHOD = {
    # possible user types (created_by.type/created_by.value)
    "user": ["H", "R"],
    "batchuploader": ["N", "M"],
    "migration": ["migration"],
}

ACCESS_TYPE = {
    "OPEN_ACCESS": ["6"],
    "RESTRICTED_NATIONAL_LICENSE": ["5"],
    "RESTRICTED_PERPETUAL_ACCESS_SUBSCRIPTION": ["1"],
    "RESTRICTED_PERPETUAL_ACCESS_BACKFILES": ["7"],
    "RESTRICTED_PACKAGE_DEAL": ["8"],
    "RESTRICTED_UNDEFINED": ["9"],
}

ITEMS_MEDIUMS = {
    "PAPER": ["PAPER"],
    "EBOOK": ["EBOOK"],
    "CDROM": ["CDROM", "CD-ROM"],
    "DVD": ["DVD VIDEO", "DVD"],
    "VHS": ["VHS"],
    "ONLINE": ["EBOOK"],
}

# can be inconsistent with the medium types
# materials used in the copyrights and licenses
MATERIALS = [
    "addendum",
    "additional material",
    "data",
    "e-proceedings",
    "ebook",
    "editorial note",
    "erratum",
    "preprint",
    "publication",
    "reprint",
    "software",
    "translation",
]

# WARNING! this should be consistent with document_identifiers_materials.json
IDENTIFIERS_MEDIUM_TYPES = {
    "ELECTRONIC": ["ELECTRONIC VERSION", "EBOOK"],
    "HARDBACK": ["PRINT VERSION, HARDBACK"],
    "PAPERBACK": ["PRINT VERSION, PAPERBACK"],
    "PRINT_VERSION": ["PRINT VERSION", "PRINT VERSION, SPIRAL-BOUND"],
    "CD_ROM": ["CDROM", "CD-ROM"],
    "AUDIOBOOK": ["AUDIOBOOK"],
    "AUDIO_CD": ["AUDIO CD"],
    "DISKETTE": ["DISKETTE"],
    "DVD": ["DVD"],
    "VHS": ["VHS"],
}

APPLICABILITY = {
    "APPLICABLE": ["APPLICABLE AT CERN", "APPLICABLE"],
    "NO_LONGER_APPLICABLE": ["NO LONGER APPLICABLE"],
    "NOT_YET_APPLICABLE": ["NOT YET APPLICABLE"],
}

# Got the values from https://cds.cern.ch/kb/export?kbname=Experiments
# (same as for the vocabulary)
EXPERIMENTS = {
    "ATLAS": ["ATLAS"],
    "EA_IRRAD_MIXED_FIELD": ["EA-IRRAD Mixed-Field"],
    "EA_IRRAD_PROTON": ["EA-IRRAD Proton"],
    "IS270": ["IS270"],
    "LHC_B_OLD_NOT_USED": ["### LHC-B old not used!"],
    "ACCESS": ["ACCESS"],
    "AD_1": ["AD-1"],
    "AD_2": ["AD-2"],
    "AD_3": ["AD-3"],
    "AD_4": ["AD-4"],
    "AD_5": ["AD-5"],
    "AD_6": ["AD-6"],
    "AD_7": ["AD-7"],
    "AD_8": ["AD-8"],
    "AL_01": ["AL-01"],
    "ALEPH": ["ALEPH"],
    "ALICE": ["ALICE"],
    "ALPHA": ["ALPHA"],
    "AMS_RE1": ["AMS-RE1"],
    "ANNA_TETES": ["ANNA TETES"],
    "ANTARES": ["ANTARES"],
    "ATHENA": ["ATHENA"],
    "ATRAP": ["ATRAP"],
    "AWAKE": ["Awake", "AWAKE"],
    "BABAR": ["BABAR"],
    "BELLE": ["BELLE"],
    "BETS": ["BETS"],
    "BOREX": ["BOREX"],
    "CALET": ["CALET"],
    "CALICE": ["CALICE"],
    "CAPRICE_RE2": ["CAPRICE-RE2"],
    "CAST": ["CAST"],
    "CLIC_DETECTORS": ["CLIC Detectors"],
    "CLIC_TEST_FACILITY": ["CLIC TEST FACILITY"],
    "CLICDP": ["CLICdp"],
    "CLOUD_PS215": ["CLOUD PS215"],
    "CMS": ["CMS"],
    "CNGS": ["CNGS"],
    "CNGS1": ["CNGS1"],
    "CNGS2": ["CNGS2"],
    "COMPASS_P297": ["COMPASS P297"],
    "COMPASSP297": ["COMPASSP297"],
    "COMPUTING": ["COMPUTING"],
    "COSMOLEP": ["COSMOLEP"],
    "CREAM": ["CREAM"],
    "CTF2": ["CTF2"],
    "CTF3": ["CTF3"],
    "DELPHI": ["DELPHI"],
    "DEUTERON_PRODUCTION_IN_PP_COLLISONS": [
        "Deuteron production in pp collisons"
    ],
    "DIRAC": ["DIRAC"],
    "DREAM": ["DREAM"],
    "E51": ["E51"],
    "E52": ["E52"],
    "E53": ["E53"],
    "E54": ["E54"],
    "E55": ["E55"],
    "E55A": ["E55a"],
    "E56": ["E56"],
    "E57": ["E57"],
    "E58": ["E58"],
    "ECC": ["ECC"],
    "EEE": ["EEE"],
    "EGEE": ["EGEE"],
    "EISA": ["EISA"],
    "ELEC": ["ELEC"],
    "ELENA": ["ELENA"],
    "EMI": ["EMI"],
    "EMU01": ["EMU01"],
    "EMU02": ["EMU02"],
    "EMU03": ["EMU03"],
    "EMU04": ["EMU04"],
    "EMU05": ["EMU05"],
    "EMU06": ["EMU06"],
    "EMU07": ["EMU07"],
    "EMU08": ["EMU08"],
    "EMU09": ["EMU09"],
    "EMU10": ["EMU10"],
    "EMU11": ["EMU11"],
    "EMU12": ["EMU12"],
    "EMU13": ["EMU13"],
    "EMU14": ["EMU14"],
    "EMU15": ["EMU15"],
    "EMU16": ["EMU16"],
    "EMU17": ["EMU17"],
    "EMU18": ["EMU18"],
    "EMU19": ["EMU19"],
    "EMU20": ["EMU20"],
    "ESI": ["ESI"],
    "EUDET": ["EUDET"],
    "FASER": ["FASER"],
    "FCC": ["FCC"],
    "FELIX": ["FELIX"],
    "GIF": ["GIF"],
    "GR02": ["GR02"],
    "GR03": ["GR03"],
    "GR04": ["GR04"],
    "GR1": ["GR1"],
    "H1": ["H1"],
    "H8_RD22": ["H8-RD22"],
    "HARP": ["HARP"],
    "HERD": ["HERD"],
    "HIRADMAT": ["HiRadMat"],
    "HYBRID_PHOTODETECTOR": ["HYBRID PHOTODETECTOR", "HybridPhotodetectors"],
    "I32": ["I32"],
    "ICANOE": ["ICANOE"],
    "ICARUS": ["ICARUS"],
    "IRRAD_1_TO_5": ["IRRAD 1 TO 5"],
    "IS03": ["IS03"],
    "IS10": ["IS10"],
    "IS100": ["IS100"],
    "IS110": ["IS110"],
    "IS120": ["IS120"],
    "IS130": ["IS130"],
    "IS140": ["IS140"],
    "IS150": ["IS150"],
    "IS160": ["IS160"],
    "IS170": ["IS170"],
    "IS180": ["IS180"],
    "IS181": ["IS181"],
    "IS190": ["IS190"],
    "IS20": ["IS20"],
    "IS200": ["IS200"],
    "IS21": ["IS21"],
    "IS210": ["IS210"],
    "IS220": ["IS220"],
    "IS230": ["IS230"],
    "IS240": ["IS240"],
    "IS260": ["IS260"],
    "IS30": ["IS30"],
    "IS300": ["IS300"],
    "IS301": ["IS301"],
    "IS302": ["IS302"],
    "IS303": ["IS303"],
    "IS304": ["IS304"],
    "IS305": ["IS305"],
    "IS306": ["IS306"],
    "IS307": ["IS307"],
    "IS308": ["IS308"],
    "IS309": ["IS309"],
    "IS31": ["IS31"],
    "IS310": ["IS310"],
    "IS311": ["IS311"],
    "IS312": ["IS312"],
    "IS313": ["IS313"],
    "IS314": ["IS314"],
    "IS315": ["IS315"],
    "IS316": ["IS316"],
    "IS317": ["IS317"],
    "IS318": ["IS318"],
    "IS319": ["IS319"],
    "IS320": ["IS320"],
    "IS321": ["IS321"],
    "IS322": ["IS322"],
    "IS323": ["IS323"],
    "IS324": ["IS324"],
    "IS325": ["IS325"],
    "IS326": ["IS326"],
    "IS327": ["IS327"],
    "IS328": ["IS328"],
    "IS329": ["IS329"],
    "IS330": ["IS330"],
    "IS331": ["IS331"],
    "IS332": ["IS332"],
    "IS333": ["IS333"],
    "IS334": ["IS334"],
    "IS335": ["IS335"],
    "IS336": ["IS336"],
    "IS337": ["IS337"],
    "IS338": ["IS338"],
    "IS339": ["IS339"],
    "IS340": ["IS340"],
    "IS341": ["IS341"],
    "IS342": ["IS342"],
    "IS343": ["IS343"],
    "IS344": ["IS344"],
    "IS345": ["IS345"],
    "IS346": ["IS346"],
    "IS347": ["IS347"],
    "IS348": ["IS348"],
    "IS349": ["IS349"],
    "IS350": ["IS350"],
    "IS351": ["IS351"],
    "IS352": ["IS352"],
    "IS353": ["IS353"],
    "IS354": ["IS354"],
    "IS355": ["IS355"],
    "IS356": ["IS356"],
    "IS357": ["IS357"],
    "IS358": ["IS358"],
    "IS359": ["IS359"],
    "IS360": ["IS360"],
    "IS361": ["IS361"],
    "IS362": ["IS362"],
    "IS363": ["IS363"],
    "IS364": ["IS364"],
    "IS365": ["IS365"],
    "IS366": ["IS366"],
    "IS367": ["IS367"],
    "IS368": ["IS368"],
    "IS369": ["IS369"],
    "IS370": ["IS370"],
    "IS371": ["IS371"],
    "IS372": ["IS372"],
    "IS373": ["IS373"],
    "IS374": ["IS374"],
    "IS375": ["IS375"],
    "IS376": ["IS376"],
    "IS377": ["IS377"],
    "IS378": ["IS378"],
    "IS379": ["IS379"],
    "IS380": ["IS380"],
    "IS381": ["IS381"],
    "IS382": ["IS382"],
    "IS383": ["IS383"],
    "IS384": ["IS384"],
    "IS385": ["IS385"],
    "IS386": ["IS386"],
    "IS387": ["IS387"],
    "IS388": ["IS388"],
    "IS389": ["IS389"],
    "IS390": ["IS390"],
    "IS391": ["IS391"],
    "IS392": ["IS392"],
    "IS393": ["IS393"],
    "IS394": ["IS394"],
    "IS395": ["IS395"],
    "IS396": ["IS396"],
    "IS397": ["IS397"],
    "IS398": ["IS398"],
    "IS399": ["IS399"],
    "IS40": ["IS40"],
    "IS400": ["IS400"],
    "IS401": ["IS401"],
    "IS402": ["IS402"],
    "IS403": ["IS403"],
    "IS404": ["IS404"],
    "IS405": ["IS405"],
    "IS406": ["IS406"],
    "IS407": ["IS407"],
    "IS408": ["IS408"],
    "IS409": ["IS409"],
    "IS410": ["IS410"],
    "IS411": ["IS411"],
    "IS412": ["IS412"],
    "IS413": ["IS413"],
    "IS414": ["IS414"],
    "IS415": ["IS415"],
    "IS416": ["IS416"],
    "IS417": ["IS417"],
    "IS418": ["IS418"],
    "IS419": ["IS419"],
    "IS420": ["IS420"],
    "IS421": ["IS421"],
    "IS422": ["IS422"],
    "IS423": ["IS423"],
    "IS424": ["IS424"],
    "IS425": ["IS425"],
    "IS426": ["IS426"],
    "IS427": ["IS427"],
    "IS428": ["IS428"],
    "IS429": ["IS429"],
    "IS430": ["IS430"],
    "IS431": ["IS431"],
    "IS432": ["IS432"],
    "IS433": ["IS433"],
    "IS434": ["IS434"],
    "IS435": ["IS435"],
    "IS436": ["IS436"],
    "IS437": ["IS437"],
    "IS438": ["IS438"],
    "IS439": ["IS439"],
    "IS440": ["IS440"],
    "IS441": ["IS441"],
    "IS442": ["IS442"],
    "IS443": ["IS443"],
    "IS444": ["IS444"],
    "IS445": ["IS445"],
    "IS446": ["IS446"],
    "IS447": ["IS447"],
    "IS448": ["IS448"],
    "IS449": ["IS449"],
    "IS450": ["IS450"],
    "IS451": ["IS451"],
    "IS452": ["IS452"],
    "IS453": ["IS453"],
    "IS454": ["IS454"],
    "IS455": ["IS455"],
    "IS456": ["IS456"],
    "IS457": ["IS457"],
    "IS458": ["IS458"],
    "IS459": ["IS459"],
    "IS460": ["IS460"],
    "IS461": ["IS461"],
    "IS462": ["IS462"],
    "IS463": ["IS463"],
    "IS464": ["IS464"],
    "IS465": ["IS465"],
    "IS466": ["IS466"],
    "IS467": ["IS467"],
    "IS468": ["IS468"],
    "IS469": ["IS469"],
    "IS470": ["IS470"],
    "IS471": ["IS471"],
    "IS472": ["IS472"],
    "IS473": ["IS473"],
    "IS474": ["IS474"],
    "IS475": ["IS475"],
    "IS476": ["IS476"],
    "IS477": ["IS477"],
    "IS478": ["IS478"],
    "IS479": ["IS479"],
    "IS480": ["IS480"],
    "IS481": ["IS481"],
    "IS482": ["IS482"],
    "IS483": ["IS483"],
    "IS484": ["IS484"],
    "IS485": ["IS485"],
    "IS486": ["IS486"],
    "IS487": ["IS487"],
    "IS488": ["IS488"],
    "IS489": ["IS489"],
    "IS490": ["IS490"],
    "IS491": ["IS491"],
    "IS492": ["IS492"],
    "IS493": ["IS493"],
    "IS494": ["IS494"],
    "IS495": ["IS495"],
    "IS496": ["IS496"],
    "IS497": ["IS497"],
    "IS498": ["IS498"],
    "IS499": ["IS499"],
    "IS50": ["IS50"],
    "IS500": ["IS500"],
    "IS501": ["IS501"],
    "IS502": ["IS502"],
    "IS503": ["IS503"],
    "IS504": ["IS504"],
    "IS505": ["IS505"],
    "IS506": ["IS506"],
    "IS507": ["IS507"],
    "IS508": ["IS508"],
    "IS509": ["IS509"],
    "IS510": ["IS510"],
    "IS511": ["IS511"],
    "IS512": ["IS512"],
    "IS513": ["IS513"],
    "IS514": ["IS514"],
    "IS515": ["IS515"],
    "IS516": ["IS516"],
    "IS517": ["IS517"],
    "IS518": ["IS518"],
    "IS519": ["IS519"],
    "IS520": ["IS520"],
    "IS521": ["IS521"],
    "IS522": ["IS522"],
    "IS523": ["IS523"],
    "IS524": ["IS524"],
    "IS525": ["IS525"],
    "IS526": ["IS526"],
    "IS527": ["IS527"],
    "IS528": ["IS528"],
    "IS529": ["IS529"],
    "IS530": ["IS530"],
    "IS531": ["IS531"],
    "IS532": ["IS532"],
    "IS533": ["IS533"],
    "IS534": ["IS534"],
    "IS535": ["IS535"],
    "IS536": ["IS536"],
    "IS537": ["IS537"],
    "IS538": ["IS538"],
    "IS539": ["IS539"],
    "IS540": ["IS540"],
    "IS541": ["IS541"],
    "IS542": ["IS542"],
    "IS543": ["IS543"],
    "IS544": ["IS544"],
    "IS545": ["IS545"],
    "IS546": ["IS546"],
    "IS547": ["IS547"],
    "IS548": ["IS548"],
    "IS549": ["IS549"],
    "IS550": ["IS550"],
    "IS551": ["IS551"],
    "IS552": ["IS552"],
    "IS553": ["IS553"],
    "IS554": ["IS554"],
    "IS555": ["IS555"],
    "IS556": ["IS556"],
    "IS557": ["IS557"],
    "IS558": ["IS558"],
    "IS559": ["IS559"],
    "IS560": ["IS560"],
    "IS561": ["IS561"],
    "IS562": ["IS562"],
    "IS563": ["IS563"],
    "IS564": ["IS564"],
    "IS565": ["IS565"],
    "IS566": ["IS566"],
    "IS567": ["IS567"],
    "IS568": ["IS568"],
    "IS569": ["IS569"],
    "IS570": ["IS570"],
    "IS571": ["IS571"],
    "IS572": ["IS572"],
    "IS573": ["IS573"],
    "IS574": ["IS574"],
    "IS575": ["IS575"],
    "IS576": ["IS576"],
    "IS577": ["IS577"],
    "IS578": ["IS578"],
    "IS579": ["IS579"],
    "IS580": ["IS580"],
    "IS581": ["IS581"],
    "IS582": ["IS582"],
    "IS583": ["IS583"],
    "IS584": ["IS584"],
    "IS585": ["IS585"],
    "IS586": ["IS586"],
    "IS587": ["IS587"],
    "IS588": ["IS588"],
    "IS589": ["IS589"],
    "IS590": ["IS590"],
    "IS591": ["IS591"],
    "IS592": ["IS592"],
    "IS593": ["IS593"],
    "IS594": ["IS594"],
    "IS595": ["IS595"],
    "IS596": ["IS596"],
    "IS597": ["IS597"],
    "IS598": ["IS598"],
    "IS599": ["IS599"],
    "IS60": ["IS60"],
    "IS600": ["IS600"],
    "IS601": ["IS601"],
    "IS602": ["IS602"],
    "IS603": ["IS603"],
    "IS604": ["IS604"],
    "IS605": ["IS605"],
    "IS606": ["IS606"],
    "IS607": ["IS607"],
    "IS608": ["IS608"],
    "IS609": ["IS609"],
    "IS610": ["IS610"],
    "IS611": ["IS611"],
    "IS612": ["IS612"],
    "IS613": ["IS613"],
    "IS614": ["IS614"],
    "IS615": ["IS615"],
    "IS616": ["IS616"],
    "IS617": ["IS617"],
    "IS618": ["IS618"],
    "IS619": ["IS619"],
    "IS620": ["IS620"],
    "IS621": ["IS621"],
    "IS622": ["IS622"],
    "IS623": ["IS623"],
    "IS624": ["IS624"],
    "IS625": ["IS625"],
    "IS626": ["IS626"],
    "IS627": ["IS627"],
    "IS628": ["IS628"],
    "IS629": ["IS629"],
    "IS630": ["IS630"],
    "IS631": ["IS631"],
    "IS632": ["IS632"],
    "IS633": ["IS633"],
    "IS634": ["IS634"],
    "IS635": ["IS635"],
    "IS636": ["IS636"],
    "IS637": ["IS637"],
    "IS638": ["IS638"],
    "IS639": ["IS639"],
    "IS640": ["IS640"],
    "IS646": ["IS646"],
    "IS647": ["IS647"],
    "IS648": ["IS648"],
    "IS649": ["IS649"],
    "IS650": ["is650"],
    "IS651": ["IS651"],
    "IS652": ["IS652"],
    "IS653": ["IS653"],
    "IS654": ["IS654", "Is654"],
    "IS655": ["Is655", "IS655"],
    "IS656": ["IS656"],
    "IS657": ["IS657"],
    "IS70": ["IS70"],
    "IS80": ["IS80"],
    "IS81": ["IS81"],
    "IS82": ["IS82"],
    "IS83": ["IS83"],
    "IS84": ["IS84"],
    "IS90": ["IS90"],
    "ISOLDE": ["ISOLDE"],
    "ISOLDE_COLLABORATION": ["ISOLDE COLLABORATION"],
    "ISOLDE_RABBIT": ["ISOLDE RABBIT"],
    "ISOLDE2": ["ISOLDE2"],
    "KASCADE": ["KASCADE"],
    "L3": ["L3"],
    "LAA": ["LAA"],
    "LANNDD": ["LANNDD"],
    "LASER_ION_SOURCE": ["LASER ION SOURCE"],
    "LBNF_DUNE": ["LBNF/DUNE"],
    "LCG": ["LCG"],
    "LEP5": ["LEP5"],
    "LEP6": ["LEP6"],
    "LHCB": ["LHCB"],
    "LHCF": ["LHCF"],
    "LHEC": ["LHeC"],
    "LIL": ["LIL"],
    "LINEAR_COLLIDER_DETECTOR": ["Linear Collider Detector"],
    "LPM": ["LPM"],
    "MACFLY": ["MACFLY"],
    "MADMAX": ["MadMax"],
    "MEDIPIX": ["MEDIPIX"],
    "MEDIPIX_3": ["MEDIPIX 3"],
    "MICROSCINT": ["microScint"],
    "MINOS": ["MINOS"],
    "MOEDAL": ["MoEDAL"],
    "NA1": ["NA1"],
    "NA10": ["NA10"],
    "NA11": ["NA11"],
    "NA12": ["NA12"],
    "NA12_2": ["NA12/2"],
    "NA120": ["NA120"],
    "NA120_LC": ["NA120-LC"],
    "NA13": ["NA13"],
    "NA14": ["NA14"],
    "NA14_2": ["NA14/2"],
    "NA15": ["NA15"],
    "NA16": ["NA16"],
    "NA17": ["NA17"],
    "NA18": ["NA18"],
    "NA19": ["NA19"],
    "NA2": ["NA2"],
    "NA20": ["NA20"],
    "NA21": ["NA21"],
    "NA22": ["NA22"],
    "NA23": ["NA23"],
    "NA24": ["NA24"],
    "NA25": ["NA25"],
    "NA26": ["NA26"],
    "NA27": ["NA27"],
    "NA28": ["NA28"],
    "NA29": ["NA29"],
    "NA3": ["NA3"],
    "NA30": ["NA30"],
    "NA31": ["NA31"],
    "NA31_2": ["NA31/2"],
    "NA32": ["NA32"],
    "NA33": ["NA33"],
    "NA34": ["NA34"],
    "NA34_2": ["NA34/2"],
    "NA34_3": ["NA34/3"],
    "NA35": ["NA35"],
    "NA36": ["NA36"],
    "NA37": ["NA37"],
    "NA38": ["NA38"],
    "NA39": ["NA39"],
    "NA4": ["NA4"],
    "NA40": ["NA40"],
    "NA41": ["NA41"],
    "NA42": ["NA42"],
    "NA43": ["NA43"],
    "NA43_2": ["NA43/2"],
    "NA44": ["NA44"],
    "NA45": ["NA45"],
    "NA45_2": ["NA45/2"],
    "NA46": ["NA46"],
    "NA47": ["NA47"],
    "NA48": ["NA48"],
    "NA48_1": ["NA48/1"],
    "NA48_2": ["NA48/2"],
    "NA48_3": ["NA48/3"],
    "NA49": ["NA49"],
    "NA5": ["NA5"],
    "NA50": ["NA50"],
    "NA51": ["NA51"],
    "NA52": ["NA52"],
    "NA53": ["NA53"],
    "NA54": ["NA54"],
    "NA55": ["NA55"],
    "NA56": ["NA56"],
    "NA57": ["NA57"],
    "NA58": ["NA58"],
    "NA59": ["NA59"],
    "NA6": ["NA6"],
    "NA60": ["NA60"],
    "NA61": ["NA61"],
    "NA62": ["NA62"],
    "NA63": ["NA63"],
    "NA64": ["NA64"],
    "NA65": ["NA65"],
    "NA7": ["NA7"],
    "NA700": ["NA700"],
    "NA8": ["NA8"],
    "NA9": ["NA9"],
    "NGS": ["NGS"],
    "NP01": ["NP01"],
    "NP02": ["NP02"],
    "NP03": ["NP03"],
    "NP04": ["NP04"],
    "NP05": ["NP05"],
    "NP06": ["NP06"],
    "NP07": ["NP07"],
    "NP4": ["NP4"],
    "NP5": ["NP5"],
    "NTOF": ["nTOF"],
    "NTOF_COLLABORATION": ["nTOF COLLABORATION"],
    "NTOF1": ["nTOF1"],
    "NTOF10": ["nTOF10"],
    "NTOF11": ["nTOF11"],
    "NTOF12": ["nTOF12"],
    "NTOF13": ["nTOF13"],
    "NTOF14": ["nTOF14"],
    "NTOF15": ["nTOF15"],
    "NTOF16": ["nTOF16"],
    "NTOF17": ["nTOF17"],
    "NTOF18": ["nTOF18"],
    "NTOF19": ["nTOF19"],
    "NTOF2": ["nTOF2"],
    "NTOF20": ["nTOF20"],
    "NTOF21": ["nTOF21"],
    "NTOF22": ["nTOF22"],
    "NTOF23": ["nTOF23"],
    "NTOF24": ["nTOF24"],
    "NTOF25": ["nTOF25"],
    "NTOF26": ["nTOF26"],
    "NTOF27": ["nTOF27"],
    "NTOF28": ["nTOF28"],
    "NTOF29": ["nTOF29"],
    "NTOF3": ["nTOF3"],
    "NTOF30": ["nTOF30"],
    "NTOF31": ["nTOF31"],
    "NTOF32": ["nTOF32"],
    "NTOF33": ["nTOF33"],
    "NTOF34": ["nTOF34"],
    "NTOF35": ["nTOF35"],
    "NTOF36": ["nTOF36"],
    "NTOF37": ["nTOF37"],
    "NTOF38": ["nTOF38"],
    "NTOF39": ["nTOF39"],
    "NTOF4": ["nTOF4"],
    "NTOF40": ["nTOF40"],
    "NTOF41": ["nTOF41"],
    "NTOF42": ["nTOF42"],
    "NTOF43": ["nTOF43"],
    "NTOF44": ["nTOF44"],
    "NTOF45": ["nTOF45"],
    "NTOF46": ["nTOF46"],
    "NTOF47": ["nTOF47"],
    "NTOF48": ["nTOF48"],
    "NTOF49": ["nTOF49"],
    "NTOF5": ["nTOF5"],
    "NTOF50": ["nTOF50"],
    "NTOF51": ["nTOF51"],
    "NTOF52": ["nTOF52"],
    "NTOF53": ["nTOF53"],
    "NTOF54": ["nTOF54"],
    "NTOF55": ["nTOF55"],
    "NTOF56": ["nTOF56"],
    "NTOF57": ["nTOF57"],
    "NTOF58": ["nTOF58"],
    "NTOF59": ["nTOF59"],
    "NTOF6": ["nTOF6"],
    "NTOF60": ["nTOF60"],
    "NTOF61": ["nTOF61"],
    "NTOF62": ["nTOF62"],
    "NTOF7": ["nTOF7"],
    "NTOF8": ["nTOF8"],
    "NTOF9": ["nTOF9"],
    "NUCLEON": ["NUCLEON"],
    "OFFLINE": ["OFFLINE"],
    "OPAL": ["OPAL"],
    "OPENLAB": ["OPENLAB"],
    "OPERA": ["OPERA"],
    "OSQAR": ["OSQAR"],
    "OUTREACH": ["OUTREACH"],
    "P_AUGER_RE3": ["P-AUGER-RE3"],
    "P348": ["P348"],
    "P349": ["P349"],
    "PHENIX": ["PHENIX"],
    "PHYSICS_BEYOND_COLLIDERS_STUDY": ["Physics Beyond Colliders Study"],
    "PLAFOND": ["PLAFOND"],
    "PS131": ["PS131"],
    "PS132": ["PS132"],
    "PS135": ["PS135"],
    "PS136": ["PS136"],
    "PS137": ["PS137"],
    "PS140": ["PS140"],
    "PS141": ["PS141"],
    "PS142": ["PS142"],
    "PS143": ["PS143"],
    "PS144": ["PS144"],
    "PS145": ["PS145"],
    "PS146": ["PS146"],
    "PS147": ["PS147"],
    "PS148": ["PS148"],
    "PS149": ["PS149"],
    "PS150": ["PS150"],
    "PS151": ["PS151"],
    "PS152": ["PS152"],
    "PS153": ["PS153"],
    "PS154": ["PS154"],
    "PS155": ["PS155"],
    "PS156": ["PS156"],
    "PS157": ["PS157"],
    "PS158": ["PS158"],
    "PS159": ["PS159"],
    "PS160": ["PS160"],
    "PS161": ["PS161"],
    "PS162": ["PS162"],
    "PS163": ["PS163"],
    "PS164": ["PS164"],
    "PS165": ["PS165"],
    "PS166": ["PS166"],
    "PS167": ["PS167"],
    "PS168": ["PS168"],
    "PS169": ["PS169"],
    "PS170": ["PS170"],
    "PS171": ["PS171"],
    "PS172": ["PS172"],
    "PS173": ["PS173"],
    "PS174": ["PS174"],
    "PS175": ["PS175"],
    "PS176": ["PS176"],
    "PS177": ["PS177"],
    "PS178": ["PS178"],
    "PS179": ["PS179"],
    "PS180": ["PS180"],
    "PS181": ["PS181"],
    "PS182": ["PS182"],
    "PS183": ["PS183"],
    "PS184": ["PS184"],
    "PS185": ["PS185"],
    "PS185_2": ["PS185/2"],
    "PS185_3": ["PS185/3"],
    "PS186": ["PS186"],
    "PS187": ["PS187"],
    "PS188": ["PS188"],
    "PS189": ["PS189"],
    "PS190": ["PS190"],
    "PS191": ["PS191"],
    "PS192": ["PS192"],
    "PS193": ["PS193"],
    "PS194": ["PS194"],
    "PS194_2": ["PS194/2"],
    "PS194_3": ["PS194/3"],
    "PS195": ["PS195"],
    "PS196": ["PS196"],
    "PS197": ["PS197"],
    "PS198": ["PS198"],
    "PS199": ["PS199"],
    "PS200": ["PS200"],
    "PS201": ["PS201"],
    "PS202": ["PS202"],
    "PS203": ["PS203"],
    "PS204": ["PS204"],
    "PS205": ["PS205"],
    "PS206": ["PS206"],
    "PS207": ["PS207"],
    "PS208": ["PS208"],
    "PS209": ["PS209"],
    "PS210": ["PS210"],
    "PS211": ["PS211"],
    "PS212": ["PS212"],
    "PS213": ["PS213"],
    "PS214": ["PS214"],
    "PS215": ["PS215"],
    "PS97": ["PS97"],
    "PVLAS": ["PVLAS"],
    "R107": ["R107"],
    "R108": ["R108"],
    "R109": ["R109"],
    "R110": ["R110"],
    "R207": ["R207"],
    "R208": ["R208"],
    "R209": ["R209"],
    "R210": ["R210"],
    "R211": ["R211"],
    "R301": ["R301"],
    "R401": ["R401"],
    "R406": ["R406"],
    "R407": ["R407"],
    "R409": ["R409"],
    "R410": ["R410"],
    "R411": ["R411"],
    "R414": ["R414"],
    "R415": ["R415"],
    "R416": ["R416"],
    "R417": ["R417"],
    "R418": ["R418"],
    "R419": ["R419"],
    "R420": ["R420"],
    "R421": ["R421"],
    "R422": ["R422"],
    "R501": ["R501"],
    "R605": ["R605"],
    "R606": ["R606"],
    "R607": ["R607"],
    "R608": ["R608"],
    "R702": ["R702"],
    "R703": ["R703"],
    "R704": ["R704"],
    "R805": ["R805"],
    "R806": ["R806"],
    "R807": ["R807"],
    "R808": ["R808"],
    "RD_1": ["RD-1"],
    "RD_10": ["RD-10"],
    "RD_11": ["RD-11"],
    "RD_12": ["RD-12"],
    "RD_13": ["RD-13"],
    "RD_14": ["RD-14"],
    "RD_15": ["RD-15"],
    "RD_16": ["RD-16"],
    "RD_17": ["RD-17"],
    "RD_18": ["RD-18"],
    "RD_19": ["RD-19"],
    "RD_2": ["RD-2"],
    "RD_20": ["RD-20"],
    "RD_3": ["RD-3"],
    "RD_4": ["RD-4"],
    "RD_5": ["RD-5"],
    "RD_6": ["RD-6"],
    "RD_7": ["RD-7"],
    "RD_8": ["RD-8"],
    "RD_9": ["RD-9"],
    "RD21": ["RD21"],
    "RD22": ["RD22"],
    "RD23": ["RD23"],
    "RD24": ["RD24"],
    "RD25": ["RD25"],
    "RD26": ["RD26"],
    "RD27": ["RD27"],
    "RD28": ["RD28"],
    "RD29": ["RD29"],
    "RD30": ["RD30"],
    "RD31": ["RD31"],
    "RD32": ["RD32"],
    "RD33": ["RD33"],
    "RD34": ["RD34"],
    "RD35": ["RD35"],
    "RD36": ["RD36"],
    "RD37": ["RD37"],
    "RD38": ["RD38"],
    "RD39": ["RD39"],
    "RD40": ["RD40"],
    "RD41": ["RD41"],
    "RD42": ["RD42"],
    "RD43": ["RD43"],
    "RD44": ["RD44"],
    "RD45": ["RD45"],
    "RD46": ["RD46"],
    "RD47": ["RD47"],
    "RD48": ["RD48"],
    "RD49": ["RD49"],
    "RD50": ["RD50"],
    "RD51": ["RD51"],
    "RD52": ["RD52"],
    "RD53": ["RD53"],
    "RE_25": ["RE 25"],
    "RE1": ["RE1"],
    "RE10": ["RE10"],
    "RE11": ["RE11"],
    "RE12": ["RE12"],
    "RE13": ["RE13"],
    "RE14": ["RE14"],
    "RE15": ["RE15"],
    "RE16": ["RE16"],
    "RE17": ["RE17"],
    "RE18": ["RE18"],
    "RE19": ["RE19"],
    "RE2": ["RE2"],
    "RE20": ["RE20"],
    "RE21": ["RE21"],
    "RE22": ["RE22"],
    "RE23": ["RE23"],
    "RE24": ["RE24"],
    "RE25": ["RE25"],
    "RE26": ["RE26"],
    "RE27": ["RE27"],
    "RE28": ["RE28"],
    "RE29": ["RE29"],
    "RE2A": ["RE2A"],
    "RE2B": ["RE2B"],
    "RE3": ["RE3"],
    "RE30": ["RE30"],
    "RE31": ["RE31"],
    "RE32": ["RE32"],
    "RE33": ["RE33"],
    "RE34": ["RE34"],
    "RE35": ["RE35"],
    "RE36": ["RE36"],
    "RE37": ["RE37"],
    "RE38": ["RE38"],
    "RE39": ["RE39"],
    "RE4": ["RE4"],
    "RE40": ["RE40"],
    "RE5": ["RE5"],
    "RE6": ["RE6"],
    "RE7": ["RE7"],
    "RE8": ["RE8"],
    "RE9": ["RE9"],
    "ROG": ["ROG"],
    "S0": ["S0"],
    "S1": ["S1"],
    "S10": ["S10"],
    "S100": ["S100"],
    "S101": ["S101"],
    "S102": ["S102"],
    "S103": ["S103"],
    "S104": ["S104"],
    "S105": ["S105"],
    "S106": ["S106"],
    "S107": ["S107"],
    "S108": ["S108"],
    "S109": ["S109"],
    "S11": ["S11"],
    "S110": ["S110"],
    "S111": ["S111"],
    "S112": ["S112"],
    "S113": ["S113"],
    "S114": ["S114"],
    "S115": ["S115"],
    "S116": ["S116"],
    "S117": ["S117"],
    "S118": ["S118"],
    "S119": ["S119"],
    "S12": ["S12"],
    "S120": ["S120"],
    "S121": ["S121"],
    "S122": ["S122"],
    "S123": ["S123"],
    "S124": ["S124"],
    "S125": ["S125"],
    "S126": ["S126"],
    "S127": ["S127"],
    "S128": ["S128"],
    "S129": ["S129"],
    "S13": ["S13"],
    "S130": ["S130"],
    "S131": ["S131"],
    "S132": ["S132"],
    "S133": ["S133"],
    "S134": ["S134"],
    "S135": ["S135"],
    "S136": ["S136"],
    "S137": ["S137"],
    "S138": ["S138"],
    "S139": ["S139"],
    "S14": ["S14"],
    "S140": ["S140"],
    "S144": ["S144"],
    "S145": ["S145"],
    "S146": ["S146"],
    "S147": ["S147"],
    "S148": ["S148"],
    "S15": ["S15"],
    "S16": ["S16"],
    "S17": ["S17"],
    "S18": ["S18"],
    "S19": ["S19"],
    "S2": ["S2"],
    "S20": ["S20"],
    "S21": ["S21"],
    "S22": ["S22"],
    "S23": ["S23"],
    "S24": ["S24"],
    "S25": ["S25"],
    "S26": ["S26"],
    "S27": ["S27"],
    "S28": ["S28"],
    "S29": ["S29"],
    "S2A": ["S2a"],
    "S3": ["S3"],
    "S30": ["S30", "S30%"],
    "S31": ["S31"],
    "S31B": ["S31b"],
    "S32": ["S32"],
    "S33": ["S33"],
    "S34": ["s34"],
    "S35": ["S35"],
    "S36": ["S36"],
    "S37": ["S37"],
    "S38": ["S38"],
    "S38A": ["S38a"],
    "S39": ["S39"],
    "S39_AND_S39A": ["S39-and-S39a"],
    "S4": ["S4"],
    "S40": ["S40"],
    "S41": ["S41"],
    "S42": ["S42"],
    "S43": ["S43"],
    "S44": ["S44"],
    "S44A": ["S44a"],
    "S45": ["S45"],
    "S46": ["S46"],
    "S47": ["S47"],
    "S48": ["S48"],
    "S49": ["S49"],
    "S5": ["S5"],
    "S50": ["S50"],
    "S51": ["S51"],
    "S52": ["S52"],
    "S53": ["S53"],
    "S54": ["S54"],
    "S55": ["S55"],
    "S56": ["S56"],
    "S57": ["S57"],
    "S58": ["S58"],
    "S59": ["S59"],
    "S6": ["S6"],
    "S60": ["S60"],
    "S61": ["S61"],
    "S62": ["S62"],
    "S63": ["S63"],
    "S64": ["S64"],
    "S65": ["S65"],
    "S66": ["S66"],
    "S67": ["S67"],
    "S68": ["S68"],
    "S69": ["S69"],
    "S7": ["s7"],
    "S70": ["S70"],
    "S71": ["S71"],
    "S72": ["S72"],
    "S73": ["S73"],
    "S74": ["S74"],
    "S75": ["S75"],
    "S76": ["S76"],
    "S77": ["S77"],
    "S78": ["S78"],
    "S79": ["S79"],
    "S80": ["S80"],
    "S81": ["S81"],
    "S82": ["S82"],
    "S83": ["S83"],
    "S84": ["S84"],
    "S85": ["S85"],
    "S86": ["S86"],
    "S87": ["S87"],
    "S88": ["S88"],
    "S89": ["S89"],
    "S9": ["S9"],
    "S90": ["S90"],
    "S91": ["S91"],
    "S92": ["S92"],
    "S93": ["S93"],
    "S94": ["S94"],
    "S95": ["S95"],
    "S96": ["S96"],
    "S97": ["S97"],
    "S98": ["S98"],
    "S99": ["S99"],
    "SATAN": ["SATAN"],
    "SBN_ICARUS": ["SBN/ICARUS"],
    "SC21": ["SC21"],
    "SC50": ["SC50"],
    "SC52": ["SC52"],
    "SC53": ["SC53"],
    "SC55": ["SC55"],
    "SC57": ["SC57"],
    "SC58": ["SC58"],
    "SC59": ["SC59"],
    "SC60": ["SC60"],
    "SC63": ["SC63"],
    "SC64": ["SC64"],
    "SC65": ["SC65"],
    "SC66": ["SC66"],
    "SC67": ["SC67"],
    "SC68": ["SC68"],
    "SC69": ["SC69"],
    "SC70": ["SC70"],
    "SC71": ["SC71"],
    "SC72": ["SC72"],
    "SC73": ["SC73"],
    "SC74": ["SC74"],
    "SC75": ["SC75"],
    "SC76": ["SC76"],
    "SC77": ["SC77"],
    "SC78": ["SC78"],
    "SC79": ["SC79"],
    "SC80": ["SC80"],
    "SC81": ["SC81"],
    "SC82": ["SC82"],
    "SC83": ["SC83"],
    "SC84": ["SC84"],
    "SC85": ["SC85"],
    "SC86": ["SC86"],
    "SC87": ["SC87"],
    "SC88": ["SC88"],
    "SC89": ["SC89"],
    "SC90": ["SC90"],
    "SC91": ["SC91"],
    "SC92": ["SC92"],
    "SC93": ["SC93"],
    "SC94": ["SC94"],
    "SC95": ["SC95"],
    "SC96": ["SC96"],
    "SC97": ["SC97"],
    "SC98": ["SC98"],
    "SHIP": ["SHiP"],
    "SLHC_PP": ["SLHC-PP"],
    "SLIM5": ["SLIM5"],
    "SPECIAL": ["SPECIAL"],
    "SUB_EXPERIMENT": ["SUB EXPERIMENT"],
    "T209": ["T209"],
    "T211": ["T211"],
    "T227": ["T227"],
    "T236": ["T236"],
    "T237": ["T237"],
    "T239": ["T239"],
    "T248": ["T248"],
    "T250": ["T250"],
    "TCC2__INB_AREA": ["TCC2 (INB AREA)"],
    "TERA": ["TERA"],
    "TESLA": ["TESLA"],
    "TEST": ["TEST"],
    "TESTISA": ["TESTISA"],
    "TOP_EXPERIMENT": ["TOP_EXPERIMENT"],
    "TOTEM": ["TOTEM"],
    "TRIGGER": ["TRIGGER"],
    "TT40__INB_AREA": ["TT40 (INB AREA)"],
    "UA1": ["UA1"],
    "UA2": ["UA2"],
    "UA3": ["UA3"],
    "UA4": ["UA4"],
    "UA4_2": ["UA4/2"],
    "UA5": ["UA5"],
    "UA5_2": ["UA5/2"],
    "UA6": ["UA6"],
    "UA7": ["UA7"],
    "UA8": ["UA8"],
    "UA9": ["UA9"],
    "UNDEFINED": ["UNDEFINED"],
    "UNOSAT": ["UNOSAT"],
    "WA1": ["WA1"],
    "WA1_2": ["WA1/2"],
    "WA10": ["WA10"],
    "WA100": ["WA100"],
    "WA101": ["WA101"],
    "WA102": ["WA102"],
    "WA103": ["WA103"],
    "WA104": ["WA104"],
    "WA105": ["WA105"],
    "WA11": ["WA11"],
    "WA12": ["WA12"],
    "WA13": ["WA13"],
    "WA14": ["WA14"],
    "WA15": ["WA15"],
    "WA16": ["WA16"],
    "WA17": ["WA17"],
    "WA18": ["WA18"],
    "WA18_2": ["WA18/2"],
    "WA19": ["WA19"],
    "WA2": ["WA2"],
    "WA20": ["WA20"],
    "WA21": ["WA21"],
    "WA22": ["WA22"],
    "WA23": ["WA23"],
    "WA24": ["WA24"],
    "WA25": ["WA25"],
    "WA26": ["WA26"],
    "WA27": ["WA27"],
    "WA28": ["WA28"],
    "WA29": ["WA29"],
    "WA3": ["WA3"],
    "WA30": ["WA30"],
    "WA31": ["WA31"],
    "WA32": ["WA32"],
    "WA33": ["WA33"],
    "WA34": ["WA34"],
    "WA35": ["WA35"],
    "WA36": ["WA36"],
    "WA37": ["WA37"],
    "WA38": ["WA38"],
    "WA39": ["WA39"],
    "WA4": ["WA4"],
    "WA40": ["WA40"],
    "WA41": ["WA41"],
    "WA42": ["WA42"],
    "WA43": ["WA43"],
    "WA44": ["WA44"],
    "WA45": ["WA45"],
    "WA46": ["WA46"],
    "WA47": ["WA47"],
    "WA48": ["WA48"],
    "WA49": ["WA49"],
    "WA5": ["WA5"],
    "WA50": ["WA50"],
    "WA51": ["WA51"],
    "WA52": ["WA52"],
    "WA53": ["WA53"],
    "WA54": ["WA54"],
    "WA55": ["WA55"],
    "WA56": ["WA56"],
    "WA57": ["WA57"],
    "WA58": ["WA58"],
    "WA59": ["WA59"],
    "WA6": ["WA6"],
    "WA60": ["WA60"],
    "WA61": ["WA61"],
    "WA62": ["WA62"],
    "WA63": ["WA63"],
    "WA64": ["WA64"],
    "WA65": ["WA65"],
    "WA66": ["WA66"],
    "WA67": ["WA67"],
    "WA68": ["WA68"],
    "WA69": ["WA69"],
    "WA7": ["WA7"],
    "WA70": ["WA70"],
    "WA71": ["WA71"],
    "WA72": ["WA72"],
    "WA73": ["WA73"],
    "WA74": ["WA74"],
    "WA75": ["WA75"],
    "WA76": ["WA76"],
    "WA77": ["WA77"],
    "WA78": ["WA78"],
    "WA79": ["WA79"],
    "WA8": ["WA8"],
    "WA80": ["WA80"],
    "WA81": ["WA81"],
    "WA82": ["WA82"],
    "WA83": ["WA83"],
    "WA84": ["WA84"],
    "WA85": ["WA85"],
    "WA86": ["WA86"],
    "WA87": ["WA87"],
    "WA88": ["WA88"],
    "WA89": ["WA89"],
    "WA9": ["WA9"],
    "WA90": ["WA90"],
    "WA91": ["WA91"],
    "WA92": ["WA92"],
    "WA93": ["WA93"],
    "WA94": ["WA94"],
    "WA95": ["WA95"],
    "WA96": ["WA96"],
    "WA97": ["WA97"],
    "WA98": ["WA98"],
    "WA99": ["WA99"],
    "WA99_2": ["WA99/2"],
    "WIZARD": ["WIZARD"],
    "WIZCAL": ["WIZCAL"],
    "ZEUS": ["ZEUS"],
}

ARXIV_CATEGORIES = [
    "astro-ph",
    "astro-ph.CO",
    "astro-ph.EP",
    "astro-ph.GA",
    "astro-ph.HE",
    "astro-ph.IM",
    "astro-ph.SR",
    "cond-mat",
    "cond-mat.dis-nn",
    "cond-mat.mes-hall",
    "cond-mat.mtrl-sci",
    "cond-mat.other",
    "cond-mat.quant-gas",
    "cond-mat.soft",
    "cond-mat.stat-mech",
    "cond-mat.str-el",
    "cond-mat.supr-con",
    "cs",
    "cs.AI",
    "cs.AR",
    "cs.CC",
    "cs.CE",
    "cs.CG",
    "cs.CL",
    "cs.CR",
    "cs.CV",
    "cs.CY",
    "cs.DB",
    "cs.DC",
    "cs.DL",
    "cs.DM",
    "cs.DS",
    "cs.ET",
    "cs.FL",
    "cs.GL",
    "cs.GR",
    "cs.GT",
    "cs.HC",
    "cs.IR",
    "cs.IT",
    "cs.LG",
    "cs.LO",
    "cs.MA",
    "cs.MM",
    "cs.MS",
    "cs.NA",
    "cs.NE",
    "cs.NI",
    "cs.OH",
    "cs.OS",
    "cs.PF",
    "cs.PL",
    "cs.RO",
    "cs.SC",
    "cs.SD",
    "cs.SE",
    "cs.SI",
    "cs.SY",
    "econ",
    "econ.EM",
    "eess",
    "eess.AS",
    "eess.IV",
    "eess.SP",
    "gr-qc",
    "hep-ex",
    "hep-lat",
    "hep-ph",
    "hep-th",
    "math",
    "math-ph",
    "math.AC",
    "math.AG",
    "math.AP",
    "math.AT",
    "math.CA",
    "math.CO",
    "math.CT",
    "math.CV",
    "math.DG",
    "math.DS",
    "math.FA",
    "math.GM",
    "math.GN",
    "math.GR",
    "math.GT",
    "math.HO",
    "math.IT",
    "math.KT",
    "math.LO",
    "math.MG",
    "math.MP",
    "math.NA",
    "math.NT",
    "math.OA",
    "math.OC",
    "math.PR",
    "math.QA",
    "math.RA",
    "math.RT",
    "math.SG",
    "math.SP",
    "math.ST",
    "nlin",
    "nlin.AO",
    "nlin.CD",
    "nlin.CG",
    "nlin.PS",
    "nlin.SI",
    "nucl-ex",
    "nucl-th",
    "physics",
    "physics.acc-ph",
    "physics.ao-ph",
    "physics.app-ph",
    "physics.atm-clus",
    "physics.atom-ph",
    "physics.bio-ph",
    "physics.chem-ph",
    "physics.class-ph",
    "physics.comp-ph",
    "physics.data-an",
    "physics.ed-ph",
    "physics.flu-dyn",
    "physics.gen-ph",
    "physics.geo-ph",
    "physics.hist-ph",
    "physics.ins-det",
    "physics.med-ph",
    "physics.optics",
    "physics.plasm-ph",
    "physics.pop-ph",
    "physics.soc-ph",
    "physics.space-ph",
    "q-bio",
    "q-bio.BM",
    "q-bio.CB",
    "q-bio.GN",
    "q-bio.MN",
    "q-bio.NC",
    "q-bio.OT",
    "q-bio.PE",
    "q-bio.QM",
    "q-bio.SC",
    "q-bio.TO",
    "q-fin",
    "q-fin.CP",
    "q-fin.EC",
    "q-fin.GN",
    "q-fin.MF",
    "q-fin.PM",
    "q-fin.PR",
    "q-fin.RM",
    "q-fin.ST",
    "q-fin.TR",
    "quant-ph",
    "stat",
    "stat.AP",
    "stat.CO",
    "stat.ME",
    "stat.ML",
    "stat.OT",
    "stat.TH",
]

INSTITUTIONS = [
    "KEK",
    "CERN",
    "DESY",
    "SLAC",
    "Fermilab",
    "Cornell",
    "BNL",
    "ANL",
]


ACCELERATORS = ["SPS", "R&D", "OTHER", "RADFAC", "RE"]

SUBJECT_CLASSIFICATION_EXCEPTIONS = [
    "PACS",
    "CERN LIBRARY",
    "CERN YELLOW REPORT",
]

EXTERNAL_SYSTEM_IDENTIFIERS = [
    "DCL",
    "DESY",
    "DOE",
    "EBL",
    "FIZ",
    "HAL",
    "IEECONF",
    "INDICO.CERN.CH",
    "INIS",
    "INSPIRE",
    "KEK",
    "LHCLHC",
    "SAFARI",
    "SCEM",
    "UDCCERN",
    "WAI01",
]

EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE = [
    "ARXIV",
    "CERN ANNUAL REPORT",
    "HTTP://INSPIREHEP.NET/OAI2D",
    "SLAC",
    "SLACCONF",
    "SPIRES",
]


def mapping(field_map, val, raise_exception=False, default_val=None):
    """
    Maps the old value to a new one according to the map.

    important: the maps values must be uppercase, in order to catch all the
    possible values in the field
    :param field_map: one of the maps specified
    :param val: old value
    :param raise_exception if mapping should raise exception when value does
           not match
    :raises UnexpectedValue
    :return: output value matched in map
    """
    if isinstance(val, str):
        val = val.strip()
    if val:
        if isinstance(field_map, dict):
            for k, v in field_map.items():
                if val.upper() in v:
                    return k
        elif isinstance(field_map, list):
            if val in field_map:
                return val
        elif default_val:
            return default_val
        if raise_exception:
            raise UnexpectedValue
