..
    Copyright (C) 2019 CERN.

    CDS-ILS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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



