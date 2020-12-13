# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""This is the CERN Document Server source code overlay for InvenioILS"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "Sphinx>=3.1.1",
    "mock>=2.0.0",
    "pytest-invenio>=1.4.0",
    "pytest-mock>=1.6.0",
    "pytest-random-order>=0.5.4",
]

setup_requires = ["Babel>=2.8.0"]

extras_require = {"docs": ["Sphinx>=1.5.1"], "tests": tests_require}

extras_require["all"] = []
for name, reqs in extras_require.items():
    extras_require["all"].extend(reqs)

install_requires = [
    "iniconfig<1.1.0",  # remove when fixed on PyPi
    "Flask-BabelEx>=0.9.3",
    "uwsgi>=2.0",
    "uwsgitop>=0.11",
    "uwsgi-tools>=1.1.1",
    "fuzzywuzzy>=0.18.0",
    "python-ldap>=3.2.0,<3.3.0",
    "invenio-oauthclient>=1.3.5,<1.4.0",
    "invenio-app-ils[lorem,elasticsearch7,postgresql]==1.0.0a21",
    "sentry-sdk>=0.10.2",
    # migrator deps
    "cds-dojson==0.9.0",
    "lxml>=3.5.0",
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("cds_ils", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="cds-ils",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="CDS-ILS InvenioILS Invenio",
    license="MIT",
    author="CERN CDS Team",
    author_email="cds.support@cern.ch",
    url="https://github.com/CERNDocumentServer/cds-ils",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": ["cds-ils = invenio_app.cli:cli"],
        "flask.commands": [
            "user-testing = cds_ils.cli:user_testing",
            "ldap-users = cds_ils.ldap.cli:ldap_users",
            "migration = cds_ils.migrator.cli:migration",
            "importer = cds_ils.importer.cli:importer",
            "fixtures = cds_ils.cli:fixtures",
            "covers = cds_ils.cli:covers",
        ],
        "invenio_db.models": [
            "cds_ils_ldap = cds_ils.ldap.models",
            "cds_ils_importer = cds_ils.importer.models",
        ],
        "invenio_admin.views": [
            "cds_ils_ldap_sync = cds_ils.ldap.admin:ldap_sync",
            "cds_ils_importer_tasks = cds_ils.importer.admin:importer_tasks",
            "cds_ils_records = cds_ils.importer.admin:importer_records",
        ],
        "invenio_base.api_apps": ["cds_ils = cds_ils.ext:CdsIls"],
        "invenio_base.apps": ["cds_ils_app = cds_ils.ext:CdsIls"],
        "invenio_base.blueprints": [
            "cds_ils_admin = cds_ils.ldap.admin:blueprint",
        ],
        "invenio_base.api_blueprints": [
            "cds_ils_patron_loans = cds_ils.patrons.views:create_patron_loans_blueprint",
            "cds_ils_legacy = cds_ils.literature.views:legacy_blueprint",
            "cds_ils_logout = cds_ils.authentication.views:cern_oauth_blueprint",
            "cds_ils_importer = cds_ils.importer.views:create_importer_blueprint",
        ],
        "invenio_config.module": ["cds_ils = cds_ils.config"],
        "invenio_celery.tasks": [
            "cds_ils_tasks = cds_ils.literature.tasks",
            "cds_ils_ldap_tasks = cds_ils.ldap.tasks",
            "cds_ils_mail_tasks = cds_ils.mail.tasks",
        ],
        "invenio_i18n.translations": ["messages = cds_ils"],
        "invenio_access.actions": [
            "retrieve_patron_loans_access_action = "
            "cds_ils.patrons.permissions:retrieve_patron_loans_access_action"
        ],
        "cds_ils.importers": [
            "cds = cds_ils.importer.providers.cds.importer:CDSImporter",
            "springer = cds_ils.importer.providers.springer.importer:SpringerImporter",
            "ebl = cds_ils.importer.providers.ebl.importer:EBLImporter",
            "safari = cds_ils.importer.providers.safari.importer:SafariImporter",
        ],
        "cds_ils.importer.base": [
            "base = cds_ils.importer.providers.rules.base",
        ],
        "cds_ils.importer.models": [
            "cds_book = cds_ils.importer.providers.cds.models.book:model",
            "cds_standard = cds_ils.importer.providers.cds.models.standard:model",
            "springer_document = cds_ils.importer.providers.springer.springer:model",
            "ebl_document = cds_ils.importer.providers.ebl.ebl:model",
            "safari_document = cds_ils.importer.providers.safari.safari:model",
        ],
        "cds_ils.importer.series_models": [
            "ils_serial = cds_ils.importer.providers.cds.models.serial:model",
            "ils_multipart = cds_ils.importer.providers.cds.models.multipart:model",
            "ils_journal = cds_ils.importer.providers.cds.models.journal:model",
        ],
        "cds_ils.importer.cds.base": [
            "base = cds_ils.importer.providers.cds.rules.base",
        ],
        "cds_ils.importer.cds.document": [
            "book = cds_ils.importer.providers.cds.rules.book",
            "standard = cds_ils.importer.providers.cds.rules.standard",
        ],
        "cds_ils.importer.document": [
            "cds = cds_ils.importer.providers.cds.rules.book",
            "springer = cds_ils.importer.providers.springer.rules.document",
            "ebl = cds_ils.importer.providers.ebl.rules.document",
            "safari = cds_ils.importer.providers.safari.rules.document",
        ],
        "cds_ils.importer.series": [
            "serial = cds_ils.importer.providers.cds.rules.serial",
            "multipart = cds_ils.importer.providers.cds.rules.multipart",
            "journal = cds_ils.importer.providers.cds.rules.journal",
        ],
        "cds_ils.migrator.base": [
            "base = cds_ils.importer.providers.cds.rules.base",
        ],
        "invenio_pidstore.minters": [
            "lrecid = cds_ils.minters:legacy_recid_minter",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 3 - Alpha",
    ],
)
