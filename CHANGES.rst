..
    Copyright (C) 2019-2024 CERN.

    CDS-ILS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 3.4.0 (released 2024-11-19)

- self-checkout: integrate new dedicated endpoints

Version 3.3.0 (released 2024-11-04)

- self-checkout: move permissions check to invenio-app-ils
- importer: add `jm` as possible audiobook id
- importer: `series` word is removed only when appearing at end of the title

Version 3.2.0 (released 2024-10-22)

- search: add cross_field search type to enable AND searches across multiple fields

Version 3.1.0 (released 2024-10-01)

- global: upgrade react-invenio-app-ils
- global: add manual self-checkout
- ui: display call number on blank shelf

Version 3.0.0 (released 2024-07-02)

- global: upgrade invenio-app-ils (upgrades underlying mappings)
- config: change search query parser
- validation: add mandatory call number for call numbers

Version 2.9.0 (released 2024-05-28)

- global: add self-checkout
- patrons: reformat full names
- document: display call number in the backoffice

Version 2.8.4 (released 2024-06-12)

- overridden: hide map if wrong value is stored in shelf field

Version 2.8.3 (released 2024-05-28)

- installation: upgrade invenio-app-ils (v3.0.0rc2)
- installation: upgrade react-invenio-app-ils (v1.0.0-alpha.85)
- document: CERN Maps integration improvements
- setup: Pin flask-mail==0.9.1
- importer: providers: Update ignored fields
- tests: importer: Test cases for different types and provider priorities
- importer: Create new audiobook for document with existing e-book
- importer: ignore inspire hep oai links as identifiers
- assets: fix eslinter
- overridden: backoffice: Add Identifiers to ItemMetadata
- overridden: frontsite: DocumentDetails: Integrate MapCERN
- importer: Add video importing feature and tests
- tests: importer: Add test for importing audiobook for existing document
- importer: Add ability to import audiobooks

Version 2.8.2 (released 2024-05-13)

- eitems: add new provider (manual creation only)

Version 2.8.1 (released 2024-05-06)

- importer: fix report display (missing records)
- importer: change e-book import open access label

Version 2.8.0 (released 2024-04-25)

- installation: upgrade invenio-app-ils
- metadata: add new tags to the vocabularies
- importer: fix case sensitivity
- assets: modify homepage sections
- assets: fix responsiveness issues
- loan: adapt require before a certain date to weekends

Version 2.7.0 (released 2024-04-02)

- installation: upgrade react-invenio-app-ils

Version 2.6.1 (released 2024-04-02)

 - overridden: Handled cases where payment information is missing

Version 2.6.0 (released 2024-04-02)

- installation: upgrade react-invenio-app-ils

Version 2.5.0 (released 2024-03-04)

- installation: upgrade invenio-app-ils, react-invenio-app-ils
- ui: add custom, CERN specific names to form fields
- frontsite: update opening hours page
- config: set loan request to start in 2 days

Version 2.4.0 (released 2024-02-27)

- installation: invenio-app-ils upgrade (fix facets boolean)

Version 2.3.0 (released 2024-02-21)

- installation: invenio-app-ils upgrade (fix facets range)

Version 2.2.0 (released 2024-02-19)

- installation: invenio-app-ils upgrade

Version 2.1.0 (released 2024-02-19)

- installation: invenio-app-ils upgrade

Version 2.0.0 (released 2024-102-16)

- global: python version upgrade
- global: invenio dependencies upgrade

Version 1.2.57 (released 2023-11-30)

- assets: update homepage image

Version 1.2.56 (released 2023-11-29)

- change headline image

Version 1.2.55 (released 2023-10-19)

- global: fix SNV link

Version 1.2.54 (released 2023-10-19)

- gloabl: add SNV message for standards

Version 1.2.53 (released 2023-10-06)

- global: update library location in the footer

Version 1.2.52 (released 2023-06-22)

- global: bump react-invenio-app-ils
- global: pin Flask-WTF<1.1.0

Version 1.2.51 (released 2023-05-09)

- search: decreases ElasticSearch timeout to default (10 sec)

Version 1.2.50 (2023-05-04)

- Fix wrong token scope for CERN SSO.

Version 1.2.49 (released 2023-04-19)

- search: increases ElasticSearch timeout

Version 1.2.48 (released 2023-03-21)

- global: fixes to support OpenSearch

Version 1.2.47 (released 2023-03-10)

- mappings: introduce Opensearch mappings for v1 and v2
- bump invenio-app-ils in a Opensearch v2 compatible version

Version 1.2.46 (released 2023-01-06)

- importer: add a default language for imported book missing the language.

Version 1.2.45 (released 2022-11-11)

- importer: fix normalized title to ignore only last 'series'

Version 1.2.44 (released 2022-10-24)

- change eitems source vocabulary size

Version 1.2.41 (released 2022-10-07)

- Change location link and display text

Version 1.2.40 (released 2022-10-06)

- bump invenio-app-ils

Version 1.2.39 (released 2022-10-05)

- revert previous bump of dependencies due to missing support python version 3.6.

Version 1.2.38 (released 2022-10-03)

- udpated library location

Version 1.2.37 (released 2022-09-19)

- importer: add new provider
- importer: fix an issue with title matching
- bump dependencies

Version 1.2.34 (released 2022-08-12)

- importer: add new safari rules
- importer: add providers priority
- bump invenio-app-ils

Version 1.2.33 (released 2022-06-09)

- importer: add AMS provider to vocabulary and fix an issue with unknown providers.

Version 1.2.32 (released 2022-05-25)

- importer: change series matching to match by title first.

Version 1.2.31 (released 2022-05-06)

- importer: add series match validation on preview

Version 1.2.30 (released 2022-05-06)

- fix series matching by ISSNs

Version 1.2.29 (released 2022-05-06)

- match series by one of ISSNs

Version 1.2.28 (released 2022-04-28)

- fix importer bug to match series correctly

Version 1.2.27 (released 2022-03-31)

- update links in static pages
- fix cli to assign legacy pid
- Adds building and phone information to the footer

Version 1.2.26 (released 2022-03-10)

- fix search phrases for series volumes

Version 1.2.24 (released 2022-02-24)

- Fix bug with conference info not showing in the frontsite

Version 1.2.23 (released 2022-02-23)

- Update invenio-opendefinition

Version 1.2.22 (released 2022-02-23)

- Pin itsdangerous
- Increase max authors able to be edited in the document editor
- Fixing `et al.` display across the system


Version 1.2.20 (released 2022-02-01)

- fix wrong search guide link
- update react-invenio-app-ils and react-searchkit to latest

Version 1.2.18 (released 2022-01-18)

- importer: bugfixes
- ldap: add user deletion script
- document details: add links to external services
- global: add privacy policy page
- document: check if document exists on indexing references
- circulation: improve CSV export

Version 1.2.13 (released 2022-01-06)

- Importer:
    - improve handling errors
    - fix parsing series and documents titles
    - fix priority providers imports
    - fix indexing issues
    - fix matching by authors surnames
- Maintenance: add legacy pid minting
- Dependencies: upgrade lxml


Version 1.2.12 (released 2021-12-10)

- Importer: fix duplication of series during the import
- Importer: fix eitems import priority

Version 1.2.11 (released 2021-12-08)

- Upgrade invenio packages
- Upgrade flask + werkzeug > v2.0.0
- Upgrade various python packages
- Add custom loan search serializer
    - drop redundant loan fields
    - add item_suggestion location
- Importer: improve performance of detail page loading
- Importer: improve records matching script
- Purchase orders: automatically propagate payment information
- Alert librarian on extending loans on overbooked documents
- Fix loan requests order
- Fix alert librarian about preceding loan request during checkout
- Patron history: fix "See all" query


Version 1.2.10 (released 2021-11-16)

- Added error messages that can appear while opening a deleted task or an unexpected response from the backend
- Items on loan are now being shown again in the where to find section of the document detail page (front-office)
- Fixed inconsistencies in the preview statuses
- Importer item row now displays the title from the imported document and not the matched document
- Importer now does an extra check to validate that matched documents have equal ISBN/Title pairs, otherwise will categorize it as a partial match
- Various minor improvements from feedback that was received
    - ignore rules checkbox is un-checkable
    - Added name of imported file in history and task-details page
    - Added provider name to task details page
    - Search bar is not case sensitive anymore
    - Added pagination to importer task overview
    - Added partial matches to statistics
    - Pagination does not go back to page 1 when an action happens
    - Providers names changed
    - Backend raises exception when wrong provider is chosen
    - Statistics segment does not appear in 2 rows with large numbers anymore
- Overdue loans can now also be bulk extended
