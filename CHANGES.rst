..
    Copyright (C) 2019 CERN.

    CDS-ILS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======






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



