# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""This is the CERN Document Server source code overlay for"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('cds_books', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='cds-books',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='cds-books Invenio',
    license='MIT',
    author='`Invenio ILS flavor <http://github.com/inveniosoftware/invenio-app-ils>`.',
    author_email='cds.support@cern.ch',
    url='https://github.com/CERNDocumentServer/cds-books',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'cds-books = invenio_app.cli:cli',
        ],
        'invenio_base.apps': [
        ],
        'invenio_base.blueprints': [
            'cds_books = cds_books.theme.views:blueprint',
        ],
        'invenio_assets.webpack': [
            'cds_books_theme = cds_books.theme.webpack:theme',
        ],
        'invenio_config.module': [
            'cds_books = cds_books.config',
        ],
        'invenio_i18n.translations': [
            'messages = cds_books',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
