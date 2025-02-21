# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
"""CDS-ILS MARCXML Base fields."""

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import re
from calendar import month_name

import pycountry
from dateutil import parser
from dateutil.parser import ParserError
from dojson.errors import IgnoreKey
from dojson.utils import filter_values, flatten, for_each_value, force_list
from flask import current_app
from invenio_app_ils.relations.api import (
    EDITION_RELATION,
    LANGUAGE_RELATION,
    OTHER_RELATION,
)

from cds_ils.importer.errors import (
    ManualImportRequired,
    MissingRequiredField,
    UnexpectedValue,
)
from cds_ils.importer.providers.cds.cds import model
from cds_ils.importer.providers.cds.rules.values_mapping import (
    ACQUISITION_METHOD,
    APPLICABILITY,
    COLLECTION,
    DOCUMENT_TYPE,
    EXTERNAL_SYSTEM_IDENTIFIERS,
    EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE,
    IDENTIFIERS_MEDIUM_TYPES,
    ITEMS_MEDIUMS,
    MATERIALS,
    SERIAL,
    TAGS_TO_IGNORE,
    mapping,
)

from ...utils import build_ils_contributor
from ..helpers.decorators import filter_list_values, out_strip, replace_in_result
from ..helpers.eitems import clean_url_provider
from ..helpers.parsers import (
    clean_email,
    clean_val,
    extract_parts,
    extract_volume_number,
    get_week_start,
    is_excluded,
)


@model.over("legacy_recid", "^001")
def recid(self, key, value):
    """Record Identifier."""
    self["provider_recid"] = value
    return int(value)


@model.over("agency_code", "^003")
def agency_code(self, key, value):
    """Control number identifier."""
    if isinstance(value, str):
        return value
    else:
        raise IgnoreKey("agency_code")


@model.over("sync", "^599__")
def sync_tag(self, key, value):
    """Synchronisation tag."""
    sync_tag = clean_val("a", value, str).upper()
    if sync_tag in ["ILSSYNC", "ILSLINK"]:
        return True
    else:
        raise UnexpectedValue(subfield="a")


@model.over("created_by", "^859__")
@filter_values
def created_by(self, key, value):
    """Translates created_by to find submitter."""
    return {"_email": clean_email(clean_val("f", value, str)), "type": "user"}


@model.over("_created", "(^916__)|(^595__)")
@out_strip
def created(self, key, value):
    """Translates created information to fields."""
    _created_by = self.get("created_by", {})
    if key == "916__":
        if "s" in value:
            _created_by.update(
                {
                    "type": mapping(
                        ACQUISITION_METHOD,
                        clean_val("s", value, str, default="migration"),
                        raise_exception=True,
                        subfield="s",
                    )
                }
            )
            self["created_by"] = _created_by
            date_values = clean_val(
                "w", value, int, regex_format=r"^\d{6}$", multiple_values=True
            )
            if not date_values or not date_values[0]:
                return datetime.date.today().isoformat()
            date = min(date_values)
            if not (100000 < date < 999999):
                raise UnexpectedValue("Wrong date format", subfield="w")
            if date:
                year, week = str(date)[:4], str(date)[4:]
                date = get_week_start(int(year), int(week))
                if date < datetime.date.today():
                    return date.isoformat()
                else:
                    return datetime.date.today().isoformat()
    elif key == "595__":
        try:
            _migration = self["_migration"]
            _eitems_internal_notes = _migration.get("eitems_internal_notes", "")
            sub_a_internal_notes = clean_val(
                "a", value, str, regex_format=r"[A-Z]{3,4}[0-9]{4,6}$"
            )
            if sub_a_internal_notes:
                if not _eitems_internal_notes:
                    _eitems_internal_notes = sub_a_internal_notes
                else:
                    _eitems_internal_notes += f"; {sub_a_internal_notes}"
                _migration.update({"eitems_internal_notes": _eitems_internal_notes})
        except UnexpectedValue as e:
            pass
        try:
            sub_a = clean_val("a", value, str, regex_format=r"[A-Z]{3}[0-9]{6}$")
            if sub_a:
                source = sub_a[:3]
                self["source"] = source
                year, month = int(sub_a[3:7]), int(sub_a[7:])
                self["_created"] = datetime.date(year, month, 1).isoformat()
                raise IgnoreKey("_created")
        except UnexpectedValue as e:
            e.subfield, e.key = "a", key
            self["internal_notes"] = internal_notes(self, key, value)
            raise IgnoreKey("_created")

    raise IgnoreKey("_created")


@model.over("internal_notes", "^595__")
def internal_notes(self, key, value):
    """Translates private notes field."""
    _internal_notes = self.get("internal_notes", [])
    for v in force_list(value):
        internal_note = {"value": clean_val("a", v, str, req=True)}
        if internal_note not in _internal_notes:
            _internal_notes.append(internal_note)
    return _internal_notes


@model.over("tags", "(^980__)|(^690C_)|(^697C_)")
@out_strip
def tags(self, key, value):
    """Translates tag field - WARNING - also document type and serial field."""
    _tags = self.get("tags", [])
    for v in force_list(value):
        val_a = clean_val("a", v, str)
        val_b = clean_val("b", v, str)

        if val_a not in TAGS_TO_IGNORE:
            result_a = mapping(COLLECTION, val_a)
            if result_a:
                _tags.append(result_a) if result_a not in _tags else None
        else:
            result_a = True
        if val_b not in TAGS_TO_IGNORE:
            result_b = mapping(COLLECTION, val_b)
            if result_b:
                _tags.append(result_b) if result_b not in _tags else None
        else:
            result_b = True
        if not result_a and not result_b:
            special_serials(self, key, value)
    return _tags


@model.over("_migration", "^690C_")
def special_serials(self, key, value):
    """Translates serial fields."""
    _migration = self["_migration"]
    _serials = _migration.get("serials", [])
    for v in force_list(value):
        value_a = clean_val("a", v, str)
        if value_a and value_a == "YELLOW REPORT":
            _migration["is_yellow_report"] = True
        result_a = mapping(SERIAL, value_a)
        if result_a:
            (
                _serials.append(
                    {
                        "title": result_a,
                        "volume": None,
                        "issn": None,
                    }
                )
                if result_a not in _serials
                else None
            )
            _migration.update({"serials": _serials, "has_serial": True})
        if not result_a:
            self["document_type"] = document_type(self, key, value)
            raise IgnoreKey("_migration")
    return _migration


@model.over("document_type", "(^980__)|(^960__)")
@out_strip
def document_type(self, key, value):
    """Translates document type field."""
    _doc_type = self.get("document_type", None)

    def doc_type_mapping(val):
        if val:
            return mapping(DOCUMENT_TYPE, val, subfield="a or b")

    for v in force_list(value):
        sub_a = clean_val("a", v, str)
        sub_b = clean_val("b", v, str)
        val_a = doc_type_mapping(sub_a)
        val_b = doc_type_mapping(sub_b)

        if not val_a and not val_b and not _doc_type:
            continue

        if val_a and val_b and val_b != "STANDARD" and (val_a != val_b != _doc_type):
            raise ManualImportRequired("inconsistent doc type", subfield="a or b")
        if val_a:
            if _doc_type and _doc_type != "STANDARD" and _doc_type != val_a:
                raise ManualImportRequired("Inconsistent doc type", subfield="a")
            _doc_type = val_a
        if val_b:
            if _doc_type and val_b != "STANDARD" and _doc_type != val_b:
                raise ManualImportRequired("Inconsistent doc type", subfield="b")
            _doc_type = val_b
    return _doc_type


@model.over("authors", "(^100__)|(^700__)")
@filter_list_values
def authors(self, key, value):
    """Translates the authors field."""
    _authors = self.get("authors", [])
    item = build_ils_contributor(value)
    if item and item not in _authors:
        _authors.append(item)
    try:
        if "u" in value or "e" in value:
            other_authors_possible_values = ["et al.", "et al", "ed. et al."]
            val_u = list(force_list(value.get("u", [])))
            val_e = list(force_list(value.get("e", [])))
            other_authors_fields = val_e + val_u
            has_other_authors = [
                i for i in other_authors_possible_values if i in other_authors_fields
            ]
            if has_other_authors:
                self["other_authors"] = True

    except UnexpectedValue:
        pass
    return _authors


@model.over("authors", "^720__")
@filter_list_values
def alt_authors(self, key, value):
    """Translates the alternative authors field."""
    _authors = self.get("authors", [])
    if _authors:
        for i, v in enumerate(force_list(value)):
            _alternative_names = _authors[i].get("alternative_names", [])
            _alternative_names.append(clean_val("a", v, str))
            _authors[i].update({"alternative_names": _alternative_names})
    return _authors


@model.over("authors", "(^110)|(^710_[a_]+)")
@filter_list_values
def corporate_authors(self, key, value):
    """Translates the corporate authors field."""
    _corporate_authors = self.get("authors", [])

    for v in force_list(value):
        if key == "710__":
            if "a" in v:
                _corporate_authors.append(
                    {
                        "full_name": clean_val("a", v, str),
                        "type": "ORGANISATION",
                    }
                )
            else:
                self["authors"] = collaborations(self, key, value)
                raise IgnoreKey("corporate_authors")
        else:
            _corporate_authors.append(
                {"full_name": clean_val("a", v, str), "type": "ORGANISATION"}
            )
    return _corporate_authors


@model.over("authors", "^710__")
@replace_in_result("Collaboration", "", key="full_name")
@filter_list_values
def collaborations(self, key, value):
    """Translates collaborations."""
    _authors = self.get("authors", [])
    for v in force_list(value):
        if "g" in v:
            _authors.append(
                {"full_name": clean_val("g", v, str), "type": "ORGANISATION"}
            )
        elif "5" in v:
            _authors.append(
                {"full_name": clean_val("5", v, str), "type": "ORGANISATION"}
            )
    return _authors


@model.over("publication_info", "(^773__)")
@filter_list_values
def publication_info(self, key, value):
    """Translates publication_info field.

    if x and o subfields are present simultaneously
    it concatenates the text
    """
    _migration = self["_migration"]
    _publication_info = self.get("publication_info", [])
    for v in force_list(value):
        temp_info = {}
        pages = clean_val("c", v, str)
        if pages:
            temp_info.update(pages=pages)
        volume = clean_val("v", v, str)
        temp_info.update(
            {
                "journal_issue": clean_val("n", v, str),
                "journal_title": clean_val("p", v, str),
                "journal_volume": volume,
                "year": clean_val("y", v, int),
            }
        )

        rel_recid = clean_val("g", value, str)
        if rel_recid:
            recids = _migration.get("journal_record_legacy_recids", [])
            recids.append({"recid": rel_recid, "volume": volume})
            _migration["has_journal"] = True

        text = "{0} {1}".format(
            clean_val("o", v, str) or "", clean_val("x", v, str) or ""
        ).strip()
        if text:
            temp_info.update({"note": text})
        if temp_info:
            _publication_info.append(temp_info)

    return _publication_info


@model.over("extensions", "(^925__)")
@filter_values
def standard_review(self, key, value):
    """Translates standard_status field."""
    _extensions = self.get("extensions", {})
    applicability_list = _extensions.get("standard_review_applicability", [])
    applicability = mapping(
        APPLICABILITY,
        clean_val("i", value, str),
    )
    if applicability and applicability not in applicability_list:
        applicability_list.append(applicability)
    if "z" in value:
        try:
            check_date = clean_val("z", value, str)
            # Normalise date
            for month in month_name[1:]:
                if month.lower() in check_date.lower():
                    check_date_month = month
            check_date_year = re.findall(r"\d+", check_date)
            if len(check_date_year) > 1:
                raise UnexpectedValue(subfield="z")
            datetime_object = datetime.datetime.strptime(
                "{} 1 {}".format(check_date_month, check_date_year[0]),
                "%B %d %Y",
            )

            check_date_iso = datetime_object.date().isoformat()
            _extensions.update(
                {
                    "standard_review_checkdate": check_date_iso,
                }
            )
        except (ValueError, IndexError):
            raise UnexpectedValue(subfield="z")
    _extensions.update(
        {
            "standard_review_applicability": applicability_list,
            "standard_review_standard_validity": clean_val("v", value, str),
            "standard_review_expert": clean_val("p", value, str),
        }
    )
    return _extensions


@model.over("_migration", "(^775__)|(^787__)")
@out_strip
def related_records(self, key, value):
    """Translates related_records field.

    RELATED records
    """
    _migration = self["_migration"]
    _related = _migration["related"]
    relation_type = OTHER_RELATION.name
    relation_description = None
    try:
        if key == "775__" and "b" in value:
            description = clean_val("b", value, str)
            relation_description = description
            relation_type_tag = clean_val("x", value, str)
            if relation_type_tag:
                if relation_type_tag.lower() == "edition":
                    relation_type = EDITION_RELATION.name
                elif relation_type_tag.lower() == "language":
                    relation_type = LANGUAGE_RELATION.name

        if key == "787__" and "i" in value:
            clean_val("i", value, str, manual=True)

        new_relation = {
            "related_recid": clean_val("w", value, str, req=True),
            "relation_type": relation_type,
            "relation_description": relation_description,
        }
        if "n" in value:
            new_relation.update({"volume": clean_val("n", value, str)})
        _related.append(new_relation)
        _migration.update({"related": _related, "has_related": True})
        raise IgnoreKey("_migration")
    except ManualImportRequired as e:
        if key == "775__":
            e.subfield = "b or c"
        else:
            e.subfield = "i"
        raise e


@model.over("extensions", "^693__")
@filter_values
def accelerator_experiments(self, key, value):
    """Translates accelerator_experiments field."""
    _extensions = self.get("extensions", {})

    accelerators = _extensions.get("unit_accelerator", "")  # subfield a
    experiments = _extensions.get("unit_experiment", [])  # subfield e
    projects = _extensions.get("unit_project", [])  # subfield p

    val_a = clean_val("a", value, str)
    experiment = clean_val("e", value, str)

    project = clean_val("p", value, str)

    if not accelerators and val_a:
        accelerators = val_a
    elif val_a and val_a not in accelerators:
        accelerators += f"; {val_a}"
    if experiment and experiment not in experiments:
        experiments.append(experiment)
    if project and project not in projects:
        projects.append(project)

    _extensions.update(
        {
            "unit_accelerator": accelerators,
            "unit_experiment": experiments,
            "unit_project": projects,
        }
    )
    return _extensions


@model.over("_migration", "(^536__)")
@out_strip
def open_access(self, key, value):
    """Translate open access field.

    If the field is present, then the eitems of this record have open access
    """
    sub_r = clean_val("r", value, str)
    if sub_r and "open access" in sub_r.lower():
        self["_migration"]["eitems_open_access"] = True
    raise IgnoreKey("_migration")


@model.over("urls", "^8564_")
@filter_list_values
@for_each_value
def urls(self, key, value):
    """Translates urls field."""
    # Contains description and restriction of the url
    sub_y = clean_val("y", value, str, default="")
    # Value of the url
    sub_u = clean_val("u", value, str, req=True)
    return clean_url_provider(url_value=sub_u, url_description=sub_y, record_dict=self)


@model.over(
    "identifiers",
    "^020__",
)
@filter_list_values
def isbns(self, key, value):
    """Translates isbns fields."""
    _isbns = self.get("identifiers", [])
    for v in force_list(value):
        subfield_u = clean_val("u", v, str)
        isbn = {
            "value": clean_val("a", v, str) or clean_val("z", v, str),
            "scheme": "ISBN",
        }
        if not isbn["value"]:
            raise IgnoreKey("identifiers")
        if subfield_u:
            volume = re.search(r"(\(*v[.| ]*\d+.*\)*)", subfield_u)

            if volume:
                volume = volume.group(1)
                subfield_u = subfield_u.replace(volume, "").strip()
                existing_volume = self.get("volume")
                if existing_volume:
                    raise ManualImportRequired(subfield="u")
                self["volume"] = volume
            # WARNING! vocabulary document_identifiers_materials
            material = mapping(IDENTIFIERS_MEDIUM_TYPES, subfield_u, subfield="u")
            if material:
                isbn.update({"material": material})
        if isbn not in _isbns:
            _isbns.append(isbn)
    return _isbns


@model.over("identifiers", "^021__")
@filter_list_values
def standard_numbers(self, key, value):
    """Translates standard numbers values."""
    _identifiers = self.get("identifiers", [])
    a = clean_val("a", value, str)
    b = clean_val("b", value, str)
    sn = a or b
    if sn:
        _identifiers.append(
            {
                "value": sn,
                "scheme": "STANDARD_NUMBER",
            }
        )
        return _identifiers
    raise MissingRequiredField(subfield="a or b")


@model.over("alternative_identifiers", "(^0247_)|(^035__)|(^036__)")
@for_each_value
@filter_values
def alternative_identifiers(self, key, value):
    """Translates external_system_identifiers fields."""
    field_type = clean_val("2", value, str)
    sub_a = clean_val("a", value, str, req=True)
    indentifier_entry = {}
    if key == "0247_":
        if field_type and field_type.lower() == "doi":
            # if 0247__2 == doi it is a DOI identifier
            self["identifiers"] = dois(self, key, value)
            raise IgnoreKey("alternative_identifiers")
        elif field_type and field_type.lower() == "asin":
            raise IgnoreKey("alternative_identifiers")
        else:
            raise UnexpectedValue(
                subfield="2",
            )
    if key == "035__":
        if "CERCER" in sub_a:
            raise IgnoreKey("alternative_identifiers")
        sub_9 = clean_val("9", value, str, req=True).upper()
        if "CERCER" in sub_9:
            raise IgnoreKey("alternative_identifiers")

        if sub_9 in EXTERNAL_SYSTEM_IDENTIFIERS:
            indentifier_entry.update({"value": sub_a, "scheme": sub_9})
        elif sub_9 in EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE:
            raise IgnoreKey("external_system_identifiers")
        else:
            raise UnexpectedValue(subfield="9")
    if key == "036__":
        if "a" in value and "9" in value:
            sub_9 = clean_val("9", value, str, req=True).upper()
            if sub_9 in EXTERNAL_SYSTEM_IDENTIFIERS_TO_IGNORE:
                raise IgnoreKey("external_system_identifiers")
            indentifier_entry.update(
                {
                    "value": sub_a,
                    "scheme": clean_val("9", value, str, req=True).upper(),
                }
            )

    return indentifier_entry


@model.over("identifiers", "^0247_")
@filter_list_values
def dois(self, key, value):
    """Translates dois fields."""
    _identifiers = self.get("identifiers", [])
    dois_url_prefix = current_app.config["CDS_ILS_DOI_URL_PREFIX"]

    def _clean_doi_access(subfield):
        return (
            subfield.lower()
            .replace("(open access)", "")
            .replace("ebook", "e-book")
            .strip()
        )

    def clean_material(subfield_q):
        return re.sub(r"\([^)]*\)", "", subfield_q).strip()

    def create_eitem(subfield_a, subfield_q):
        eitems_external = self["_migration"]["eitems_external"]
        open_access = False
        if subfield_q:
            open_access = "open access" in subfield_q.lower()
            subfield_q = _clean_doi_access(subfield_q)
        eitem = {
            "url": {
                "description": subfield_q or "e-book",
                "value": dois_url_prefix.format(doi=subfield_a),
            },
            "open_access": open_access,
        }
        eitems_external.append(eitem)

    for v in force_list(value):
        subfield_q = clean_val("q", v, str)
        subfield_a = clean_val("a", v, str, req=True)
        create_eitem(subfield_a=subfield_a, subfield_q=subfield_q)
        if subfield_q:
            subfield_q = clean_material(subfield_q)

        # vocabulary controlled
        material = mapping(
            IDENTIFIERS_MEDIUM_TYPES,
            subfield_q,
            raise_exception=True,
        )
        doi = {
            "value": subfield_a,
            "material": material,
            "scheme": "DOI",
        }
        if doi not in _identifiers:
            _identifiers.append(doi)

    self["_migration"]["eitems_has_external"] = True

    return _identifiers


@model.over("identifiers", "(^037__)|(^088__)")
@filter_list_values
def report_numbers(self, key, value):
    """Translates report_numbers fields."""

    def get_value_rn(f_a, f_z, f_9, rn_obj):
        rn_obj.update({"value": f_a or f_z or f_9, "scheme": "REPORT_NUMBER"})

    _identifiers = self.get("identifiers", [])

    sub_9 = clean_val("9", value, str)
    sub_a = clean_val("a", value, str)
    sub_z = clean_val("z", value, str)

    all_empty = not (sub_z or sub_a or sub_9)

    if key == "037__":
        entry = {}
        if all_empty:
            raise MissingRequiredField(subfield="9 or a or z")

        if sub_9 in ["arXiv", "ARXIV", "arxiv"]:
            arxiv_eprints(self, key, value)
            raise IgnoreKey("identifiers")
        else:
            get_value_rn(sub_a, sub_z, sub_9, entry)
        _identifiers.append(entry)

    if key == "088__":
        entry = {}
        if "n" in value or "x" in value:
            barcodes(self, key, value)

        if all_empty and "n" not in value and "x" not in value:
            raise MissingRequiredField(subfield="9 or a or z or n or x")

        get_value_rn(sub_a, sub_z, sub_9, entry)
        _identifiers.append(entry)
    return _identifiers


@model.over("barcodes", "^088__")
@for_each_value
def barcodes(self, key, value):
    """Match barcodes of items to volumes."""
    val_n = clean_val("n", value, str)
    val_x = clean_val("x", value, str)

    _migration = self["_migration"]
    _migration["volumes"].append(
        dict(
            volume=extract_volume_number(val_n),
            barcode=val_x,
        )
    )
    raise IgnoreKey("barcodes")


@model.over("subjects", "(^037__)")
@filter_list_values
def arxiv_eprints(self, key, value):
    """Translates arxiv_eprints fields.

    output:
    {
      'alternative_identifiers': [{'scheme': 'ARXIV', 'value': `037__a`}],
    }
    """
    if key == "037__":
        _alternative_identifiers = self.get("alternative_identifiers", [])
        for v in force_list(value):
            eprint_id = clean_val("a", v, str, req=True)
            duplicated = [
                elem
                for i, elem in enumerate(_alternative_identifiers)
                if elem["value"] == eprint_id and elem["scheme"].lower() == "arxiv"
            ]
            if not duplicated:
                eprint = {"value": eprint_id, "scheme": "ARXIV"}
                _alternative_identifiers.append(eprint)
                self["alternative_identifiers"] = _alternative_identifiers
        raise IgnoreKey("subjects")


@model.over("languages", "^041__")
@for_each_value
@out_strip
def languages(self, key, value):
    """Translates languages fields."""
    lang = clean_val("a", value, str)
    if lang:
        lang = lang.lower()
    try:
        return pycountry.languages.lookup(lang).alpha_3.upper()
    except (KeyError, AttributeError, LookupError):
        raise UnexpectedValue(subfield="a")


@model.over("subjects", "(^050)|(^080__)|(^08204)|(^082__)|(^08200)")
@for_each_value
@out_strip
def subject_classification(self, key, value):
    """Translates subject classification field."""
    prev_subjects = self.get("subjects", [])
    scheme_mapping = {
        "080__": "UDC",
        "08204": "DEWEY",
        "082__": "DEWEY",
        "08200": "DEWEY",
        "050_4": "LOC",
        "050__": "LOC",
    }
    scheme = scheme_mapping[key]
    _subject_classification = {
        "value": clean_val("a", value, str, req=True),
        "scheme": scheme,
    }
    if _subject_classification not in prev_subjects:
        return _subject_classification
    else:
        raise IgnoreKey("subjects")


@model.over("keywords", "^6531_")
@for_each_value
@filter_values
def keywords(self, key, value):
    """Keywords."""
    return {
        "value": clean_val("a", value, str),
        "source": value.get("9") or value.get("g"),
    }


@model.over("conference_info", "(^111__)|(^711__)")
@filter_list_values
def conference_info(self, key, value):
    """Translates conference info."""

    def clean_conference_info_fields(v, required=True):
        """Clean the conference info fields."""
        try:
            opening_date = clean_val("9", v, str)
            closing_date = clean_val("z", v, str)
            dates = None
            if opening_date and closing_date:
                opening_date = parser.parse(opening_date)
                closing_date = parser.parse(closing_date)
                dates = "{0} - {1}".format(
                    opening_date.date().isoformat(),
                    closing_date.date().isoformat(),
                )
        except ValueError:
            raise UnexpectedValue(subfield="9 or z")

        conference_identifiers = []

        val_g = clean_val("g", v, str)
        val_i = clean_val("i", v, str)

        if val_g:
            conference_identifiers.append({"scheme": "CERN", "value": val_g})
        if val_i:
            conference_identifiers.append({"scheme": "INSPIRE_CNUM", "value": val_i})

        country_codes = clean_val("w", v, str, multiple_values=True)
        country = None
        if country_codes and country_codes[0]:
            try:
                _country = pycountry.countries.get(alpha_2=country_codes[0])
                country = str(_country.alpha_3)
            except (KeyError, AttributeError):
                raise UnexpectedValue(subfield="w")

        place = clean_val("c", v, str, req=required)

        series_numbers = clean_val("n", v, int, multiple_values=True)
        series_number = ", ".join(str(x) for x in series_numbers if x) or None

        return {
            "title": clean_val("a", v, str, req=required),
            "place": place,
            "dates": dates,
            "identifiers": conference_identifiers,
            "series": series_number,
            "country": country,
            "acronym": clean_val("x", v, str),
        }

    _conference_info = self.get("conference_info", [])
    _migration = self["_migration"]

    for v in force_list(value):
        if key == "111__":
            _conference_info.append(clean_conference_info_fields(v))
            _migration["conference_title"] = _conference_info[-1]["title"]
        else:
            # only subfield "a" is present, migrate as an alternative title
            if "a" in value and len(value) == 2:
                _alternative_titles = self.get("alternative_titles", [])
                _alternative_titles.append(
                    {
                        "value": clean_val("a", v, str, req=True),
                        "type": "ALTERNATIVE_TITLE",
                    }
                )
                self["alternative_titles"] = _alternative_titles
                raise IgnoreKey("conference_info")
            # if only 711__a and 711__x -> ignore
            elif "a" in value and "x" in value and len(value) == 3:
                acronym = clean_val("x", v, str)
                acronym_value = clean_val("a", v, str)
                if acronym and acronym.lower() != "acronym":
                    raise UnexpectedValue(subfield="x")
                raise IgnoreKey("conference_info")
            # if the field is marked as acronym, migrate
            # as conference_info
            elif "a" in value and "x" not in value and len(value) >= 3:
                _conference_info.append(clean_conference_info_fields(v, False))
    return _conference_info


@model.over("edition", "^250__")
@out_strip
def edition(self, key, value):
    """Translates edition indicator field."""
    sub_a = clean_val("a", value, str)
    if sub_a:
        return sub_a.replace("ed.", "")
    raise IgnoreKey("edition")


@model.over("imprint", "^260__")
@filter_values
def imprint(self, key, value):
    """Translates imprints fields."""
    reprint = clean_val("g", value, str)
    date_value = clean_val("c", value, str, req=True)

    if reprint:
        reprint = reprint.lower().replace("repr.", "").strip()
    try:
        date = parser.parse(date_value, default=datetime.datetime(1954, 1, 1))
        cleaned_date = date.date().isoformat()
        pub_year = str(date.date().year)
    except ParserError:
        date_range = date_value.split("-")
        if len(date_range) == 2:
            start_date = parser.parse(
                date_range[0], default=datetime.datetime(1954, 1, 1)
            )
            end_date = parser.parse(
                date_range[1], default=datetime.datetime(1954, 1, 1)
            )
            cleaned_date = (
                f"{start_date.date().isoformat()} - " f"{end_date.date().isoformat()} "
            )
            pub_year = f"{start_date.date().year} - {end_date.date().year}"
        else:
            if self["agency_code"] == "SNV":
                pub_year = str(datetime.datetime.now().year)
                cleaned_date = None
            else:
                raise UnexpectedValue(subfield="c")
    except Exception:
        raise UnexpectedValue(subfield="c")
    self["publication_year"] = pub_year
    return {
        "date": cleaned_date if cleaned_date else None,
        "place": clean_val("a", value, str),
        "publisher": clean_val("b", value, str),
        "reprint": reprint,
    }


@model.over("book_series", "^490__")
@for_each_value
def book_series(self, key, value):
    """Match barcodes to volumes."""
    val_n = clean_val("n", value, str)
    val_x = clean_val("x", value, str)

    _migration = self["_migration"]
    _migration["serials"].append(
        {
            "title": clean_val("a", value, str),
            "volume": clean_val("v", value, str),
            "issn": val_x,
        }
    )
    _migration["has_serial"] = True
    raise IgnoreKey("book_series")


@model.over("note", "^500__")
@out_strip
def note(self, key, value):
    """Translates public notes."""
    # merge all found notes
    _note = self.get("note", "")
    if _note:
        _note = "{0} \n{1}".format(_note, clean_val("a", value, str, req=True))
    else:
        _note = clean_val("a", value, str, req=True)

    return _note


@model.over("alternative_abstracts", "^520__")
@for_each_value
@out_strip
def alternative_abstracts(self, key, value):
    """Translates abstracts fields."""
    abstract = self.get("abstract", None)
    _alternative_abstracts = self.get("alternative_abstracts", [])
    if not abstract:
        # takes first abstract as main
        self["abstract"] = clean_val("a", value, str, req=True)
        raise IgnoreKey("alternative_abstracts")
    new_abstract = clean_val("a", value, str, req=True)
    return new_abstract if new_abstract not in _alternative_abstracts else None


@model.over("licenses", "^540__")
@for_each_value
@filter_values
def licenses(self, key, value):
    """Translates license fields."""
    ARXIV_LICENSE = "arxiv.org/licenses/nonexclusive-distrib/1.0/"
    _license = dict()
    # license url
    license_url = clean_val("u", value, str)

    material = mapping(
        MATERIALS,
        clean_val("3", value, str, transform="lower"),
        raise_exception=True,
        subfield="3",
    )

    if material:
        _license["material"] = material

    internal_notes = clean_val("g", value, str)
    if internal_notes:
        _license["internal_notes"] = internal_notes

    license_id = clean_val("a", value, str)
    if not license_id:
        # check if there is the URL instead of the id
        # the only known URL at the moment is ArXiv
        if license_url and ARXIV_LICENSE in license_url:
            license_id = "arXiv-nonexclusive-distrib-1.0"

    if license_id:
        _license["license"] = dict(id=license_id)
    else:
        raise UnexpectedValue()

    return _license


@model.over("copyrights", "^542__")
@for_each_value
@filter_values
def copyright(self, key, value):
    """Translates copyright fields."""
    material = mapping(
        MATERIALS,
        clean_val("3", value, str, transform="lower"),
        raise_exception=True,
        subfield="3",
    )

    return {
        "material": material,
        "holder": clean_val("d", value, str),
        "statement": clean_val("f", value, str),
        "year": clean_val("g", value, int),
        "url": clean_val("u", value, str),
    }


@model.over("table_of_content", "(^505__)|(^5050_)|(^50500)")
@flatten
@for_each_value
def table_of_content(self, key, value):
    """Translates table of content field."""
    text = "{0} -- {1}".format(
        clean_val("a", value, str) or "", clean_val("t", value, str) or ""
    ).strip()
    if text != "--":
        chapters = re.split(r"; | -- |--", text)
        chapters = [elem.strip(" ") for elem in chapters]
        return list(filter(None, chapters))
    else:
        raise UnexpectedValue(subfield="a or t")


@model.over("alternative_titles", "^242__")
@filter_list_values
def alternative_titles(self, key, value):
    """Translates title translations."""
    _alternative_titles = self.get("alternative_titles", [])
    if "a" in value:
        _alternative_titles.append(
            {
                "value": clean_val("a", value, str, req=True),
                "type": "TRANSLATED_TITLE",
                "language": "ENG",
            }
        )
    if "b" in value:
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str, req=True),
                "type": "TRANSLATED_SUBTITLE",
                "language": "ENG",
            }
        )
    return _alternative_titles


@model.over("alternative_titles", "^246__")
@filter_list_values
def alternative_titles_doc(self, key, value):
    """Alternative titles."""
    _alternative_titles = self.get("alternative_titles", [])

    if "a" in value:
        _alternative_titles.append(
            {
                "value": clean_val("a", value, str, req=True),
                "type": "ALTERNATIVE_TITLE",
            }
        )
    if "b" in value:
        _alternative_titles.append(
            {
                "value": clean_val("b", value, str, req=True),
                "type": "SUBTITLE",
            }
        )
    return _alternative_titles


@model.over("number_of_pages", "^300__")  # item
def number_of_pages(self, key, value):
    """Translates number_of_pages fields."""
    val_x = clean_val("x", value, str)
    val_a = clean_val("a", value, str)
    if val_x:
        if val_x == "volume":
            raise IgnoreKey("number_of_pages")
        elif val_x.lower() in ["phys.desc.", "phys.desc"]:
            self["physical_description"] = val_a
            raise IgnoreKey("number_of_pages")
    else:
        if is_excluded(val_a):
            raise IgnoreKey("number_of_pages")

        parts = extract_parts(val_a)
        if parts["has_extra"]:
            raise UnexpectedValue(subfield="a")
        if parts["physical_description"]:
            self["physical_description"] = parts["physical_description"]
        if parts["number_of_pages"]:
            return str(parts["number_of_pages"])
        raise UnexpectedValue(subfield="a")


@model.over("title", "^245__")
@out_strip
def title(self, key, value):
    """Translates title."""
    if "title" in self:
        raise UnexpectedValue(field=key, message="Ambiguous title")

    if "b" in value:
        _alternative_titles = self.get("alternative_titles", [])
        _alternative_titles.append(
            {"value": clean_val("b", value, str), "type": "SUBTITLE"}
        )
        self["alternative_titles"] = _alternative_titles
    return clean_val("a", value, str, req=True)


@model.over("_migration", "^340__")
@out_strip
def medium(self, key, value):
    """Translates medium."""
    _migration = self.get("_migration", {})
    item_mediums = _migration.get("item_medium", [])
    barcodes = []
    _medium = None
    val_x = value.get("x")

    if val_x:
        barcodes = [barcode for barcode in force_list(val_x) if barcode]

    val_a = clean_val("a", value, str)
    if val_a:
        _medium = mapping(
            ITEMS_MEDIUMS,
            val_a.upper().replace("-", ""),
            raise_exception=True,
            subfield="a",
        )

    for barcode in barcodes:
        current_item = {
            "barcode": barcode,
        }
        if _medium:
            current_item.update({"medium": _medium})
        if current_item not in item_mediums:
            item_mediums.append(current_item)
    if item_mediums:
        _migration.update(
            {
                "item_medium": item_mediums,
                "has_medium": True,
            }
        )
    return _migration
