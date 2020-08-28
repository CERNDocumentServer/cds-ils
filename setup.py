# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""This is the CERN Document Server source code overlay for"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()

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
    long_description=readme,
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
        "console_scripts": ["cds-ils = invenio_app.cli:cli",],
        "flask.commands": [
            "ldap-users = cds_ils.ldap.cli:ldap_users",
            "migration = cds_ils.migrator.cli:migration",
            "fixtures = cds_ils.cli:fixtures",
        ],
        "invenio_db.models": ["cds_ils = cds_ils.ldap.models",],
        "invenio_admin.views": [
            "invenio_ldap_sync = cds_ils.ldap.admin:ldap_sync",
        ],
        "invenio_base.api_apps": ["cds_ils = cds_ils.ext:CdsIls"],
        "invenio_base.apps": ["cds_ils_app = cds_ils.ext:CdsIls"],
        "invenio_base.blueprints": [
            "cds_ils = cds_ils.theme.views:blueprint",
            "cds_ils_admin = cds_ils.ldap.admin:blueprint",
        ],
        "invenio_base.api_blueprints": [
            "cds_ils_patron_loans = cds_ils.patrons.views:create_patron_loans_blueprint",
        ],
        "invenio_assets.webpack": [
            "cds_ils_theme = cds_ils.theme.webpack:theme",
        ],
        "invenio_config.module": ["cds_ils = cds_ils.config",],
        "invenio_celery.tasks": [
            "cds_ils_tasks = cds_ils.literature.tasks",
            "cds_ils_ldap_tasks = cds_ils.ldap.tasks",
        ],
        "invenio_i18n.translations": ["messages = cds_ils",],
        "invenio_access.actions": [
            "retrieve_patron_loans_access_action = "
            "cds_ils.patrons.permissions:retrieve_patron_loans_access_action"
        ],
    },
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
