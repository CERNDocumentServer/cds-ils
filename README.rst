..
    Copyright (C) 2019-2024 CERN.
    CDS-ILS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

========
 CDS-ILS
========

.. image:: https://github.com/CERNDocumentServer/cds-ils/workflows/CI/badge.svg
        :target: https://github.com/CERNDocumentServer/cds-ils/actions?query=workflow%3ACI

.. image:: https://img.shields.io/github/license/CERNDocumentServer/cds-ils.svg
        :target: https://github.com/CERNDocumentServer/cds-ils/blob/master/LICENSE

This is the CERN Document Server source code overlay for InvenioILS.

Update dependencies
-------------------

To update Python dependencies you need to run `npm install` in the target deployment environment:

.. code-block:: shell

    $ docker run -it --platform="linux/amd64" --rm -v $(pwd):/app -w /app \
        registry.cern.ch/inveniosoftware/almalinux:1 \
        sh -c "dnf install -y openldap-devel && pip install -e . && pip freeze > requirements.new.txt"

To update JS dependencies you need to run `npm install` in the target deployment environment:

.. code-block:: shell

    $ cd ui
    $ rm -rf package-lock.json node_modules
    # Run the container with x86_64 architecture and install packages
    $ docker run -it --platform="linux/amd64" --rm -v $(pwd):/app -w /app node:14-alpine sh -c "npm install"
