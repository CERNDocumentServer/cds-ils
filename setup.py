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
    "invenio-oauthclient>=1.3.4,<1.4.0",
    "invenio-app-ils[lorem,elasticsearch7,postgresql]==1.0.0a17",
    "sentry-sdk>=0.10.2",
    # migrator deps
    "invenio-migrator==1.0.0a10",
    "invenio-records-files",
    "cds-dojson@git+https://github.com/CERNDocumentServer/cds-dojson@books",
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
    keywords="cds-ils Invenio",
    license="MIT",
    author="`Invenio ILS flavor <http://github.com/inveniosoftware/invenio-app-ils>`.",
    author_email="cds.support@cern.ch",
    url="https://github.com/CERNDocumentServer/cds-ils",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": ["cds-ils = invenio_app.cli:cli"],
        "flask.commands": [
            "demo = cds_ils.cli:demo",
            "ldap-users = cds_ils.ldap.cli:ldap_users",
            "migration = cds_ils.migrator.cli:migration",
            "fixtures = cds_ils.cli:fixtures",
        ],
        "invenio_db.models": ["cds_ils = cds_ils.ldap.models"],
        "invenio_admin.views": [
            "invenio_ldap_sync = cds_ils.ldap.admin:ldap_sync"
        ],
        "invenio_base.api_apps": ["cds_ils = cds_ils.ext:CdsIls"],
        "invenio_base.apps": ["cds_ils_app = cds_ils.ext:CdsIls"],
        "invenio_base.blueprints": [
            "cds_ils = cds_ils.theme.views:blueprint",
            "cds_ils_admin = cds_ils.ldap.admin:blueprint",
        ],
        "invenio_base.api_blueprints": [
            "cds_ils_patron_loans = cds_ils.patrons.views:create_patron_loans_blueprint",
            "cds_ils_logout = cds_ils.authentication.views:cern_oauth_blueprint",
        ],
        "invenio_assets.webpack": [
            "cds_ils_theme = cds_ils.theme.webpack:theme"
        ],
        "invenio_config.module": ["cds_ils = cds_ils.config"],
        "invenio_celery.tasks": [
            "cds_ils_tasks = cds_ils.literature.tasks",
            "cds_ils_ldap_tasks = cds_ils.ldap.tasks",
        ],
        "invenio_i18n.translations": ["messages = cds_ils"],
        "invenio_access.actions": [
            "retrieve_patron_loans_access_action = "
            "cds_ils.patrons.permissions:retrieve_patron_loans_access_action"
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
