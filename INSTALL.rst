..
    Copyright (C) 2019 CERN.

    CDS-ILS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============

Start all dependent services using docker-compose (this will start PostgreSQL,
Elasticsearch 6, RabbitMQ and Redis):

.. code-block:: console

    $ docker-compose up -d

.. note::

    Make sure you have `enough virtual memory
    <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode>`_
    for Elasticsearch in Docker:

    .. code-block:: shell

        # Linux
        $ sysctl -w vm.max_map_count=262144

        # macOS
        $ screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
        <enter>
        linut00001:~# sysctl -w vm.max_map_count=262144


Next, bootstrap the instance (this will install all Python dependencies and
build all static assets):

.. code-block:: console

    $ ./scripts/bootstrap

Next, create database tables, search indexes and message queues:

.. code-block:: console

    $ ./scripts/setup

If the setup scripts fails because of missing vocabularies:

.. code-block:: console

    $ cd <your-virtualenv-path>/invenio-app-ils/invenio_app_ils
    $ invenio setup --verbose


Covers
------

If the covers are not displayed first run the server (to start celery)
and after the setup script:

.. code-block:: console

    $ ./scripts/server
    $ ./scripts/setup

Running
-------
Start the webserver and the celery worker:

.. code-block:: console

    $ ./scripts/server

Start a Python shell:

.. code-block:: console

    $ ./scripts/console

Upgrading
---------
In order to upgrade an existing instance simply run:

.. code-block:: console

    $ ./scripts/update

Testing
-------
Run the test suite via the provided script:

.. code-block:: console

    $ ./run-tests.sh

By default, end-to-end tests are skipped. You can include the E2E tests like
this:

.. code-block:: console

    $ env E2E=yes ./run-tests.sh

For more information about end-to-end testing see `pytest-invenio
<https://pytest-invenio.readthedocs.io/en/latest/usage.html#running-e2e-tests>`_

Production environment
----------------------
You can use simulate a full production environment using the
``docker-compose.full.yml``. You can start it like this:

.. code-block:: console

    $ ./docker/build-images.sh
    $ docker-compose -f docker-compose.full.yml up -d
    $ ./docker/wait-for-services.sh --full

Remember to create database tables, search indexes and message queues if not
already done:

.. code-block:: console

    $ docker-compose -f docker-compose.full.yml run --rm web-ui ./scripts/setup

In addition to the normal ``docker-compose.yml``, this one will start:

- HAProxy (load balancer) -- https://127.0.0.1 and http://127.0.0.1:8080
- Nginx (web frontend)
- UWSGI (application container)
- Celery (background task worker)
- Flower (Celery monitoring) -- http://127.0.0.1:5555
- Kibana (Elasticsearch inspection) -- http://127.0.0.1:5601
- RabbitMQ (message queue) -- http://guest:guest@127.0.0.1:15672

Installation errors
-------------------

On MacOS, if you have the error ``pg_config executable not found.``, then you need to install `postgresql` and symlink it:

.. code-block:: console

    $ brew install postgresql@13
    $ export PATH=$PATH:/opt/homebrew/opt/postgresql\@13/bin


On MacOS, if you have errors with ``cryptography`` and ``openssl``, make sure that you have OpenSSL v3:

.. code-block:: console

    $ brew install openssl@3
    $ LDFLAGS="-L/opt/homebrew/Cellar/openssl@3/3.1.0/lib" CPPFLAGS="-I/opt/homebrew/Cellar/openssl@3/3.1.0/include" pip install "cryptography==38.0.3"
