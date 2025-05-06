# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-IlS RDM Importer transformation module."""

import arrow

from ..errors import ImporterException

author_type_map = {"personal": "PERSON", "organisational": "ORGANISATION"}
author_role_map = {
    "contactperson": "CONTACT_PERSON",
    "datacollector": "DATA_COLLECTOR",
    "datacurator": "DATA_CURATOR",
    "datamanager": "DATA_MANAGER",
    "distributor": "DISTRIBUTOR",
    "editor": "EDITOR",
    "hostinginstitution": "HOSTING_INSTITUTION",
    "other": "OTHER",
    "producer": "PRODUCER",
    "projectleader": "PROJECT_LEADER",
    "projectmanager": "PROJECT_MANAGER",
    "registrationagency": "REGISTRATION_AGENCY",
    "registrationauthority": "REGISTRATION_AUTHORITY",
    "relatedperson": "RELATED_PERSON",
    "researcher": "RESEARCHER",
    "researchgroup": "RESEARCH_GROUP",
    "sponsor": "SPONSOR",
    "rightsholder": "RIGHTS_HOLDER",
    "supervisor": "SUPERVISOR",
    "workpackageleader": "WORK_PACKAGE_LEADER",
}
author_identifier_scheme_map = {"orcid": "ORCID"}
identifier_schemes_map = {
    "doi": "DOI",
    "isbn": "ISBN",
    "cds_ref": "REPORT_NUMBER",
}

alt_identifiers_schemes_map = {
    "arxiv": "ARXIV",
    "handle": "HDL",
    "inspire": "INSPIRE",
}

alt_titles_types_map = {
    "other": "OTHER",
    "subtitle": "SUBTITLE",
    "translated-title": "TRANSLATED_TITLE",
    "alternative-title": "ALTERNATIVE_TITLE",
}

document_type_map = {"publication-thesis": "BOOK"}

document_type_tags_map = {"publication-thesis": "THESIS"}

conference_identifiers_scheme_map = {"url": "OTHER", "inspire": "INSPIRE_CNUM"}


class ILSEntry:
    """Class representing ILS entry transformation from RDM."""

    def __init__(self, rdm_entry):
        """Constructor."""
        self.rdm_entry = rdm_entry
        self.rdm_metadata = self.rdm_entry["metadata"]
        super().__init__()

    def _alternative_abstracts(self):
        """Translate alternative abstracts."""
        additional_desc = self.rdm_metadata.get("additional_descriptions", [])
        abstracts = []
        for desc in additional_desc:
            if desc["type"]["id"] in ["abstract", "other", "methods", "technical-info"]:
                abstracts.append(desc["description"])
        return abstracts

    def _alternative_identifiers(self):
        """Translate alternative identifiers."""
        ids = []
        ids.append({"scheme": "CDS", "value": self.rdm_entry["id"]})
        for _id in self.rdm_metadata.get("identifiers", []):
            if _id["scheme"] in alt_identifiers_schemes_map:
                try:
                    identifier = {
                        "value": _id["identifier"],
                        "scheme": alt_identifiers_schemes_map[_id["scheme"]],
                    }
                    ids.append(identifier)
                except KeyError as e:
                    continue
        return ids

    def _alternative_titles(self):
        """Translate alternative titles."""
        additional_titles = self.rdm_metadata.get("additional_titles", [])
        alt_titles = []
        for title in additional_titles:
            is_translated_subtitle = (
                title["type"]["id"] == "subtitle" and "lang" in title
            )
            if is_translated_subtitle:
                alt_title = {
                    "value": title["title"],
                    "type": "TRANSLATED_SUBTITLE",
                    "language": title.get("lang", {}).get("id"),
                }
            else:
                alt_title = {
                    "value": title["title"],
                    "type": alt_titles_types_map[title["type"]["id"]],
                    "language": title.get("lang", {}).get("id"),
                }

            alt_title = {k: v for k, v in alt_title.items() if v}
            alt_titles.append(alt_title)

        return alt_titles

    def _authors(self):
        """Translate authors."""
        if "creators" not in self.rdm_metadata:
            raise ImporterException(description="Missing creators (authors) field.")

        def affiliations(affiliations):
            return [{"name": aff["name"]} for aff in affiliations]

        def identifiers(identifiers):
            ids = []
            for _id in identifiers:
                try:
                    new_id = {
                        "value": _id["identifier"],
                        "scheme": author_identifier_scheme_map[_id["scheme"]],
                    }
                    ids.append(new_id)
                except KeyError as e:
                    # we map only orcid
                    continue
            return ids

        authors = []
        for entry in self.rdm_metadata["creators"]:
            author = {
                "full_name": entry["person_or_org"]["name"],
                "type": author_type_map[entry["person_or_org"]["type"]],
                "affiliations": affiliations(entry.get("affiliations", [])),
                "identifiers": identifiers(
                    entry["person_or_org"].get("identifiers", [])
                ),
            }
            if "role" in entry:
                author.update({"roles": [author_role_map[entry["role"]["id"]]}])
            author = {k: v for k, v in author.items() if v}
            authors.append(author)
        return authors

    def _conference_info(self):
        """Translate conference info."""
        # "acronym": SanitizedUnicode(),
        # "dates": SanitizedUnicode(),
        # "place": SanitizedUnicode(),
        # "session_part": SanitizedUnicode(),
        # "session": SanitizedUnicode(),
        # "title": SanitizedUnicode(),
        # "identifiers":IdentifiersScheme(),

        rdm_conference = self.rdm_entry["custom_fields"].get("meeting:meeting", {})

        rdm_identifiers = rdm_conference.get("identifiers", [])
        ils_identifiers = [
            {
                "value": x["identifier"],
                "scheme": conference_identifiers_scheme_map[x["scheme"]],
            }
            for x in rdm_identifiers
        ]

        _ils_conference = {
            "acronym": rdm_conference.get("acronym"),
            "dates": rdm_conference.get("dates"),
            "place": rdm_conference.get("place"),
            "title": rdm_conference.get("title"),
            "identifiers": ils_identifiers,
        }
        ils_conf = {k: v for k, v in _ils_conference.items() if v}
        if ils_conf:
            return [ils_conf]
        return []

    def _copyrights(self):
        """Translate copyrights."""
        rdm_copyright = self.rdm_metadata.get("copyright")
        if rdm_copyright:
            return [{"statement": rdm_copyright}]
        return

    def _document_type(self):
        """Translate document type."""
        try:
            return document_type_map[self.rdm_metadata["resource_type"]["id"]]
        except KeyError as e:
            return "BOOK"

    def _edition(self):
        """Translate edition."""
        # {
        #     "title": SanitizedUnicode(),
        #     "isbn": SanitizedUnicode(
        #         validate=is_isbn,
        #         error_messages={
        #             "validator_failed": _("Please provide a valid ISBN.")
        #         },
        #     ),
        #     "pages": SanitizedUnicode(),
        #     "place": SanitizedUnicode(),
        #     "edition": SanitizedUnicode(),
        # }
        edition = (
            self.rdm_entry["custom_fields"].get("imprint:imprint", {}).get("edition")
        )
        return edition

    def _extensions(self):
        """Translate data model extensions."""
        extensions = {}
        extensions["unit_experiment"] = []
        extensions["unit_project"] = []
        extensions["unit_study"] = []
        accelerator = self.rdm_entry["custom_fields"].get("cern:accelerators")
        if accelerator:
            extensions["unit_accelerator"] = accelerator[0]["id"]

        for experiment in self.rdm_entry["custom_fields"].get("cern:experiments", []):
            extensions["unit_experiment"].append(experiment["title"]["en"])

        for project in self.rdm_entry["custom_fields"].get("cern:projects", []):
            extensions["unit_project"].append(project)
        for study in self.rdm_entry["custom_fields"].get("cern:studies", []):
            extensions["unit_study"].append(study)
        return extensions

    def _identifiers(self):
        """Translate identifiers."""
        ids = []
        doi = self.rdm_entry["pids"].get("doi")

        if doi:
            ids.append({"scheme": "DOI", "value": doi["identifier"]})

        for _id in self.rdm_metadata.get("identifiers", []):
            if _id["scheme"] in identifier_schemes_map:
                try:
                    identifier = {
                        "value": _id["identifier"],
                        "scheme": identifier_schemes_map[_id["scheme"]],
                    }
                    ids.append(identifier)
                except KeyError as e:
                    continue
        return ids

    def _imprint(self):
        """Translate imprint."""
        # {
        #     "title": SanitizedUnicode(),
        #     "isbn": SanitizedUnicode(
        #         validate=is_isbn,
        #         error_messages={
        #             "validator_failed": _("Please provide a valid ISBN.")
        #         },
        #     ),
        #     "pages": SanitizedUnicode(),
        #     "place": SanitizedUnicode(),
        #     "edition": SanitizedUnicode(),
        # }

        imprint = self.rdm_entry["custom_fields"].get("imprint:imprint", {})
        _ils_imprint = {
            "publisher": self.rdm_metadata.get("publisher"),
            "place": imprint.get("place"),
            "date": self.rdm_metadata["publication_date"],
        }
        ils_imprint = {k: v for k, v in _ils_imprint.items() if v}
        if ils_imprint:
            return ils_imprint

    def _internal_notes(self):
        """Translate internal notes."""
        rdm_notes = self.rdm_entry.get("internal_notes", [])
        ils_notes = []
        for note in rdm_notes:
            ils_notes.append({"value": note["note"]})
        if ils_notes:
            return ils_notes

    def _keywords(self):
        """Translate keywords."""
        rdm_keywords = self.rdm_metadata.get("subjects", [])
        return [{"value": x["subject"]} for x in rdm_keywords]

    def _languages(self):
        """Translate languages."""
        rdm_languages = self.rdm_metadata.get("languages", [])
        return [x["id"] for x in rdm_languages]

    def _licenses(self):
        """Translate licenses."""
        rdm_licenses = self.rdm_metadata.get("rights", [])
        ils_licenses = [{"license": {"id": x["id"].upper()}} for x in rdm_licenses]
        if ils_licenses:
            return ils_licenses

    def _number_of_pages(self):
        """Translate number of pages."""
        additional_desc = self.rdm_metadata.get("additional_descriptions", [])
        for desc in additional_desc:
            if desc["type"]["id"] == "physical-description":
                return desc["description"]

    def _other_authors(self):
        """Adds et. al. to the record."""
        # does not exist in CDS-RDM
        return

    def _publication_info(self):
        """Translate journal info."""
        # {
        #     "title": SanitizedUnicode(),
        #     "issue": SanitizedUnicode(),
        #     "volume": SanitizedUnicode(),
        #     "pages": SanitizedUnicode(),
        #     "issn": SanitizedUnicode(
        #         validate=is_issn,
        #         error_messages={
        #             "validator_failed": [_("Please provide a valid ISSN.")]
        #         },
        #     ),
        # }
        journal_info = self.rdm_entry["custom_fields"].get("journal:journal", {})
        pub_info = {
            "artid": journal_info.get("pages"),
            "journal_issue": journal_info.get("issue"),
            "journal_volume": journal_info.get("volume"),
            "journal_title": journal_info.get("title"),
            "pages": journal_info.get("pages"),
        }
        ils_pub_info = {k: v for k, v in pub_info.items() if v}
        if ils_pub_info:
            return [ils_pub_info]

    def _publication_year(self):
        """Translate publication year."""
        pub_date = self.rdm_metadata["publication_date"]
        return str(arrow.get(pub_date).year)

    def _restrictions(self):
        """Translate restrictions."""
        restricted = self.rdm_entry["access"]["record"] != "public"
        return restricted

    def _subjects(self):
        """Translates subjects."""
        # there are no translatable subjects at the moment from RDM
        # todo UDC when available
        return []

    def _toc(self):
        """Translate table of content."""
        additional_desc = self.rdm_metadata.get("additional_descriptions", [])
        toc_entries = []
        for desc in additional_desc:
            if desc["type"]["id"] in ["table-of-contents"]:
                toc_entries.append(desc["description"])
        return toc_entries

    def _tags(self):
        """Translate tags."""
        tags = []
        document_type = self.rdm_metadata["resource_type"]["id"]
        try:
            tag = document_type_tags_map[document_type]
            tags.append(tag)
        except KeyError:
            pass
        return tags

    def _urls(self):
        """Translate urls."""
        urls = []
        for _id in self.rdm_metadata.get("identifiers", []):
            if _id["scheme"] == "url":
                urls.append({"value": _id["identifier"]})
        return urls

    def _legacy_recid(self):
        """Extract legacy recid if present."""
        legacy_recid = None
        for _id in self.rdm_metadata.get("identifiers", []):
            if _id["scheme"] == "lcds":
                return _id["identifier"]
        return legacy_recid

    def metadata(self):
        """Translate all metadata."""
        record = {
            # for backwards compat with legacy
            "_migration": dict(
                eitems_external=None,
                eitems_proxy=None,
            ),
            "_eitem": self._eitem(),
            "_rdm_pid": self.rdm_entry["parent"]["id"],
            "agency_code": "SzGeCERN",
            "abstract": self.rdm_metadata.get("description"),
            "alternative_abstracts": self._alternative_abstracts(),
            "alternative_titles": self._alternative_titles(),
            "alternative_identifiers": self._alternative_identifiers(),
            "authors": self._authors(),
            "conference_info": self._conference_info(),
            "copyrights": self._copyrights(),
            "document_type": self._document_type(),
            "edition": self._edition(),
            "extensions": self._extensions(),
            "identifiers": self._identifiers(),
            "imprint": self._imprint(),
            "internal_notes": self._internal_notes(),
            "keywords": self._keywords(),
            "languages": self._languages(),
            "licenses": self._licenses(),
            "number_of_pages": self._number_of_pages(),
            "other_authors": self._other_authors(),
            "publication_info": self._publication_info(),
            "publication_year": self._publication_year(),
            "source": "CDS",
            "subjects": self._subjects(),
            "table_of_content": self._toc(),
            "tags": self._tags(),
            "title": self.rdm_metadata["title"],
            "urls": self._urls(),
        }
        entry = {k: v for k, v in record.items() if v}
        entry["legacy_recid"] = self._legacy_recid()
        return entry

    def _eitem(self):
        """Translate eitem information."""
        files = self.rdm_entry["files"]
        urls = []
        for filename, file_data in files["entries"].items():
            if file_data["ext"] in ["pdf", "doc", "docx"]:
                urls.append(
                    {"value": file_data["links"]["self"], "description": "e-book"}
                )
        return {"urls": urls}

    def _series(self):
        """Translate series information."""
        series = []
        additional_desc = self.rdm_metadata.get("additional_descriptions", [])
        # if we want "published in" then we go to related identifiers
        identifiers = self.rdm_metadata.get("related_identifiers", [])
        for desc in additional_desc:
            if desc["type"]["id"] == "series-information":
                _serial = {"title": desc["description"]}
                series.append(_serial)
        for _id in identifiers:
            if _id["scheme"] == "issn":
                _serial = {
                    "title": f"Series {_id['identifier']}",
                    "identifiers": [
                        {
                            "scheme": "ISSN",
                            "value": _id["identifier"],
                        }
                    ],
                }
                series.append(_serial)
        return series

    def build(self):
        """Build ILS record."""
        return {
            **self.metadata(),
            "restricted": self._restrictions(),
            "_serial": self._series(),
        }


class RDMToILSTransform:
    """Transformer class from RDM to ILS record."""

    def __init__(self, rdm_entry):
        """Constructor."""
        self.rdm_entry = rdm_entry
        super().__init__()

    def transform(self):
        """Transform RDM entry."""
        return ILSEntry(self.rdm_entry).build()
