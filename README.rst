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

Python dependencies are managed with `uv <https://docs.astral.sh/uv/>`_. They are declared in
``pyproject.toml`` and locked in ``uv.lock`` (commit both).

Optional dependencies are grouped in extras (``sentry``, ``xrootd``), which the production image
installs, and test tooling lives in the ``dev`` dependency group, which ``uv sync`` installs by default.

To add or change a dependency, edit ``pyproject.toml`` and then update the lock:

.. code-block:: shell

    $ uv lock --python 3.14

Existing locked versions are kept. To upgrade, use ``uv lock --upgrade`` (everything) or
``uv lock --upgrade-package <name>`` (a single package).

To update JS dependencies you need to run `npm install` in the target deployment environment:

.. code-block:: shell

    $ cd ui
    $ rm -rf package-lock.json node_modules
    # Run the container with x86_64 architecture and install packages
    $ docker run -it --platform="linux/amd64" --rm -v $(pwd):/app -w /app node:14-alpine sh -c "npm install"
