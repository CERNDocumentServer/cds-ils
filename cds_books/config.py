# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for CDS Books.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

import os

from invenio_app_ils.config import RECORDS_REST_ENDPOINTS
from invenio_app_ils.pidstore.pids import PATRON_PID_TYPE
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow.fields import Bool

from .literature.covers import build_syndetic_cover_urls
from .patrons.api import Patron
from .patrons.permissions import views_permissions_factory


def _(x):
    """Identity function used to trigger string extraction."""
    return x


def _parse_env_bool(var_name, default=None):
    if str(os.environ.get(var_name)).lower() == 'true':
        return True
    elif str(os.environ.get(var_name)).lower() == 'false':
        return False
    return default


# Search
# ======
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.environ.get('ELASTICSEARCH_PORT', '9200'))
ELASTICSEARCH_USER = os.environ.get('ELASTICSEARCH_USER')
ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD')
ELASTICSEARCH_URL_PREFIX = os.environ.get('ELASTICSEARCH_URL_PREFIX', '')
ELASTICSEARCH_USE_SSL = _parse_env_bool('ELASTICSEARCH_USE_SSL')
ELASTICSEARCH_VERIFY_CERTS = _parse_env_bool('ELASTICSEARCH_VERIFY_CERTS')

es_host_params = {
    'host': ELASTICSEARCH_HOST,
    'port': ELASTICSEARCH_PORT,
}
if ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
    es_host_params['http_auth'] = (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
if ELASTICSEARCH_URL_PREFIX:
    es_host_params['url_prefix'] = ELASTICSEARCH_URL_PREFIX
if ELASTICSEARCH_USE_SSL is not None:
    es_host_params['use_ssl'] = ELASTICSEARCH_USE_SSL
if ELASTICSEARCH_VERIFY_CERTS is not None:
    es_host_params['verify_certs'] = ELASTICSEARCH_VERIFY_CERTS

SEARCH_ELASTIC_HOSTS = [es_host_params]
"""Elasticsearch hosts configuration."""

# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/3'

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    # ('fr', _('French'))
]

# Base templates
# ==============
#: Global base template.
BASE_TEMPLATE = 'invenio_theme/page.html'
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = 'invenio_theme/page_cover.html'
#: Footer base template.
FOOTER_TEMPLATE = 'invenio_theme/footer.html'
#: Header base template.
HEADER_TEMPLATE = 'invenio_theme/header.html'
#: Settings base template.
SETTINGS_TEMPLATE = 'invenio_theme/page_settings.html'

# Theme configuration
# ===================
THEME_FRONTPAGE = False

# Email configuration
# ===================
#: Email address for support.
SUPPORT_EMAIL = "cds.support@cern.ch"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True

# Assets
# ======
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = 'flask_collect.storage.file'

# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _(
    "Welcome to CDS Books!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = 'redis://localhost:6379/1'
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True

# Celery configuration
# ====================
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

# Database
# ========
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = \
    'postgresql+psycopg2://cds-books:cds-books@localhost/cds-books'

# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = 'cds-books.com'

# Flask configuration
# ===================
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'CHANGE_ME'
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
#: TODO change me in production
APP_ALLOWED_HOSTS = [
    os.environ.get("ALLOWED_HOST", "localhost"),
    "127.0.0.1",
    os.environ.get("HOSTNAME", ""),  # fix disallowed host error during /ping
]
# OAI-PMH
# =======
OAISERVER_ID_PREFIX = 'oai:cds-books.com:'

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

DEBUG = False
DEBUG_TB_ENABLED = True
#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Sentry
# ======
LOGGING_SENTRY_LEVEL = "WARNING"
"""Sentry logging level."""

LOGGING_SENTRY_PYWARNINGS = False
"""Enable logging of Python warnings to Sentry."""

LOGGING_SENTRY_CELERY = False
"""Configure Celery to send logging to Sentry."""

SENTRY_DSN = None
"""Set SENTRY_DSN environment variable."""

SENTRY_CONFIG = {
    "environment": os.environ.get("SENTRY_ENVIRONMENT", "dev")
}

try:
    # Try to get the release tag
    from raven import fetch_git_sha

    SENTRY_CONFIG["release"] = fetch_git_sha(
        os.environ.get("DEPLOYMENT_INSTANCE_PATH")
    )
except Exception:
    pass

# LDAP configuration
# ======
CDS_BOOKS_LDAP_URL = "ldap://xldap.cern.ch"

# RECORDS REST
# ============

RECORDS_REST_ENDPOINTS[PATRON_PID_TYPE]["record_class"] = Patron

# ILS
# ==========
ILS_VIEWS_PERMISSIONS_FACTORY = views_permissions_factory

# Migrator configuration
# ======
MIGRATOR_RECORDS_DUMPLOADER_CLS = \
    'cds_books.migrator.records:CDSDocumentDumpLoader'
MIGRATOR_RECORDS_DUMP_CLS = 'cds_books.migrator.records:CDSRecordDump'

JSONSCHEMAS_SCHEMAS = [
    "acquisition",
    "document_requests",
    "documents",
    "ill",
    "ils",
    "invenio_opendefinition",
    "invenio_records_files",
    "loans",
]

ILS_LITERATURE_COVER_URLS_BUILDER = build_syndetic_cover_urls

# Namespaces for fields added to the metadata schema
ILS_RECORDS_METADATA_NAMESPACES = {
    "document": {
        "accelerator_experiments": {
            "@context": "https://cern.ch/accelerator_experiments/terms"
        },
        "standard_CERN_status": {
            "@context": "https://cern.ch/standard_CERN_status/terms"
        },
    }
}

# Fields added to the metadata schema.
ILS_RECORDS_METADATA_EXTENSIONS = {
    "document": {
        "accelerator_experiments:accelerator": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "accelerator_experiments:curated_relation": {
            "elasticsearch": "boolean",
            "marshmallow": Bool()
        },
        "accelerator_experiments:experiment": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "accelerator_experiments:institution": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "accelerator_experiments:legacy_name": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "accelerator_experiments:project": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "accelerator_experiments:study": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "standard_CERN_status:CERN_applicability": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
        "standard_CERN_status:standard_validity": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode(required=True)
        },
        "standard_CERN_status:checkdate": {
            "elasticsearch": "date",
            "marshmallow": SanitizedUnicode()
        },
        "standard_CERN_status:comment": {
            "elasticsearch": "text",
            "marshmallow": SanitizedUnicode()
        },
        "standard_CERN_status:expert": {
            "elasticsearch": "keyword",
            "marshmallow": SanitizedUnicode()
        },
    }
}
