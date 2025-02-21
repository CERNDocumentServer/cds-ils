# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for CDS-ILS.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

import copy
import os
from datetime import timedelta

from celery.schedules import crontab
from invenio_app.config import APP_DEFAULT_SECURE_HEADERS
from invenio_app_ils.circulation.config import ILS_CIRCULATION_RECORDS_REST_ENDPOINTS
from invenio_app_ils.circulation.transitions.transitions import (
    ILSItemOnLoanToItemOnLoan,
    ILSToItemOnLoan,
)
from invenio_app_ils.circulation.utils import (
    circulation_can_be_requested,
    circulation_is_loan_duration_valid,
    circulation_loan_will_expire_days,
)
from invenio_app_ils.config import CELERY_BEAT_SCHEDULE as ILS_CELERY_BEAT_SCHEDULE
from invenio_app_ils.config import RECORDS_REST_ENDPOINTS, RECORDS_REST_FACETS
from invenio_app_ils.documents.api import DOCUMENT_PID_TYPE, Document
from invenio_app_ils.eitems.api import EITEM_PID_TYPE
from invenio_app_ils.ill.api import (
    can_item_circulate,
    circulation_default_extension_duration,
    circulation_default_loan_duration,
)
from invenio_app_ils.items.api import ITEM_PID_TYPE
from invenio_app_ils.literature.api import LITERATURE_PID_TYPE
from invenio_app_ils.locations.api import LOCATION_PID_TYPE
from invenio_app_ils.patrons.api import PATRON_PID_TYPE
from invenio_app_ils.permissions import (
    authenticated_user_permission,
    backoffice_permission,
    loan_checkout_permission,
    loan_extend_circulation_permission,
    patron_owner_permission,
)
from invenio_app_ils.series.api import SERIES_PID_TYPE
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from invenio_circulation.transitions.transitions import (
    CreatedToPending,
    ItemOnLoanToItemReturned,
    ToCancelled,
)
from invenio_oauthclient.contrib import cern_openid
from invenio_records_rest.schemas.fields import SanitizedUnicode
from invenio_records_rest.utils import deny_all
from marshmallow.fields import Bool, List

from .circulation.utils import circulation_cds_extension_max_count
from .document_requests.notifications.filters import (
    document_requests_notifications_filter,
)
from .ill.notifications.filters import ill_notifications_filter
from .literature.covers import build_cover_urls
from .patrons.api import AnonymousPatron, Patron
from .patrons.indexer import PatronIndexer
from .patrons.permissions import views_permissions_factory


def _(x):
    """Identity function used to trigger string extraction."""
    return x


def _parse_env_bool(var_name, default=None):
    if str(os.environ.get(var_name)).lower() == "true":
        return True
    elif str(os.environ.get(var_name)).lower() == "false":
        return False
    return default


def query_params_modifier(extra_params):
    """Modifier for parameters to dsl Query function."""
    # The `AND` operator, by default, will return hits where the query tokens are all
    # in the same field. `cross_fields` must be applied to enable cross fields searches.
    extra_params["default_operator"] = "AND"
    # The `cross_fields` search type requires all searchable fields to have the same
    # analyzers. In the example below, `title` and `authors.full_name` must have the
    # same analyzer defined in the mappings.
    #
    # "query_string": {
    #   "query": "Theory Schwartz",
    #   "type": "cross_fields",
    #   "fields": ["title", "authors.full_name", "*"]
    #   "analyzer": "custom_analyzer"
    # }
    #
    # Explanation:
    # "((+title:theory +authors.full_name:theory) |
    #       (+authors.full_name:schwartz +title:schwartz))"
    extra_params["type"] = "cross_fields"


###############################################################################
# Search
###############################################################################
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = int(os.environ.get("ELASTICSEARCH_PORT", "9200"))
ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_URL_PREFIX = os.environ.get("ELASTICSEARCH_URL_PREFIX", "")
ELASTICSEARCH_USE_SSL = _parse_env_bool("ELASTICSEARCH_USE_SSL")
ELASTICSEARCH_VERIFY_CERTS = _parse_env_bool("ELASTICSEARCH_VERIFY_CERTS")

es_host_params = {"host": ELASTICSEARCH_HOST, "port": ELASTICSEARCH_PORT}
if ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
    es_host_params["http_auth"] = (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
if ELASTICSEARCH_URL_PREFIX:
    es_host_params["url_prefix"] = ELASTICSEARCH_URL_PREFIX
if ELASTICSEARCH_USE_SSL is not None:
    es_host_params["use_ssl"] = ELASTICSEARCH_USE_SSL
if ELASTICSEARCH_VERIFY_CERTS is not None:
    es_host_params["verify_certs"] = ELASTICSEARCH_VERIFY_CERTS

SEARCH_ELASTIC_HOSTS = [es_host_params]
"""Elasticsearch hosts configuration."""

###############################################################################
# Rate limiting
###############################################################################
#: Storage for rate limiter.
RATELIMIT_STORAGE_URL = "redis://localhost:6379/3"

###############################################################################
# I18N
###############################################################################
#: Default language
BABEL_DEFAULT_LANGUAGE = "en"
#: Default time zone
BABEL_DEFAULT_TIMEZONE = "Europe/Zurich"
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    # ('fr', _('French'))
]

###############################################################################
# Theme
###############################################################################
#: Global base template.
BASE_TEMPLATE = "invenio_theme/page.html"
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = "invenio_theme/page_cover.html"
#: Footer base template.
FOOTER_TEMPLATE = "invenio_theme/footer.html"
#: Header base template.
HEADER_TEMPLATE = "invenio_theme/header.html"
#: Settings base template.
SETTINGS_TEMPLATE = "invenio_theme/page_settings.html"

THEME_FRONTPAGE = False

###############################################################################
# Email
###############################################################################
#: Email address for support.
SUPPORT_EMAIL = "noreply@cern.ch"
#: Librarians email for internal system notifications.
ILS_MAIL_NOTIFY_MANAGEMENT_RECIPIENTS = []
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True
#: Email address for email notification sender.
MAIL_NOTIFY_SENDER = "noreply@cern.ch"

###############################################################################
# Accounts
###############################################################################
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to the CERN Library Catalogue!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/1"
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True

###############################################################################
# Celery configuration
###############################################################################
BROKER_URL = "amqp://guest:guest@localhost:5672/"
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672/"
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
#: Scheduled tasks configuration (aka cronjobs).
CELERY_BEAT_SCHEDULE = {
    **ILS_CELERY_BEAT_SCHEDULE,  # Parent config
    "anonymize_users": {
        "task": "cds_ils.ldap.tasks.anonymize_users_task",
        "schedule": crontab(minute=0, hour=22),  # every day, 10pm
    },
    "synchronize_users": {
        "task": "cds_ils.ldap.tasks.synchronize_users_task",
        "schedule": crontab(minute=0, hour=4),  # every day, 4am
    },
    "clean_importer_preview_logs": {
        "task": "cds_ils.importer.tasks.clean_preview_logs",
        "schedule": crontab(day_of_week="mon", minute=0, hour=6),
        # every Monday, 6am
    },
}

###############################################################################
# Database
###############################################################################
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://invenio:invenio@localhost/invenio"

###############################################################################
# Flask configuration
###############################################################################
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = "CHANGE_ME"
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
APP_ALLOWED_HOSTS = ["127.0.0.1"]

# if you need to render the Debugtoolbar, add 'unsafe-inline':
#   "script-src": ["'self'", "'unsafe-inline'"],
#   "style-src": ["'self'", "'unsafe-inline'"],
APP_DEFAULT_SECURE_HEADERS["content_security_policy"] = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "object-src": ["'self'"],
    "img-src": ["'self'"],
    "style-src": ["'self'"],
    "font-src": [
        "'self'",
        "data:",
        "https://fonts.gstatic.com",
        "https://fonts.googleapis.com",
    ],
}

###############################################################################
# Debug
###############################################################################
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

DEBUG = False
DEBUG_TB_ENABLED = True
#: Switches off intercept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

###############################################################################
# Sentry
###############################################################################
SENTRY_SDK = True
"""Use of sentry-python SDK, if false raven will be used."""
LOGGING_SENTRY_LEVEL = "WARNING"
"""Sentry logging level."""
LOGGING_SENTRY_PYWARNINGS = False
"""Enable logging of Python warnings to Sentry."""
LOGGING_SENTRY_CELERY = False
"""Configure Celery to send logging to Sentry."""
SENTRY_DSN = None
"""Set SENTRY_DSN environment variable."""
# Sentry uses env var SENTRY_ENVIRONMENT and SENTRY_RELEASE

###############################################################################
# OAuth
###############################################################################
OAUTH_REMOTE_APP_NAME = "cern_openid"
# common
_OAUTH_REMOTE_APP_COMMON = dict(
    request_token_params={"scope": "openid"},
    base_url=os.environ.get(
        "OAUTH_CERN_OPENID_BASE_URL",
        "https://keycloak-qa.cern.ch/auth/realms/cern",
    ),
    access_token_url=os.environ.get(
        "OAUTH_CERN_OPENID_ACCESS_TOKEN_URL",
        "https://keycloak-qa.cern.ch/auth/realms/cern/" "protocol/openid-connect/token",
    ),
    authorize_url=os.environ.get(
        "OAUTH_CERN_OPENID_AUTHORIZE_URL",
        "https://keycloak-qa.cern.ch/auth/realms/cern/" "protocol/openid-connect/auth",
    ),
)
OAUTHCLIENT_CERN_OPENID_USERINFO_URL = (
    "https://keycloak-qa.cern.ch/auth/realms/cern/" "protocol/openid-connect/userinfo"
)
OAUTHCLIENT_CERN_OPENID_ALLOWED_ROLES = ["cern-user", "librarian", "admin"]
CERN_APP_OPENID_CREDENTIALS = dict(
    consumer_key=os.environ.get("OAUTH_CERN_OPENID_CLIENT_ID", "localhost-cds-ils"),
    consumer_secret=os.environ.get("OAUTH_CERN_OPENID_CLIENT_SECRET", "<change_me>"),
)
USERPROFILES_EXTEND_SECURITY_FORMS = True
###############################################################################
# non-REST
OAUTH_REMOTE_APP = copy.deepcopy(cern_openid.REMOTE_APP)
OAUTH_REMOTE_APP["params"].update(_OAUTH_REMOTE_APP_COMMON)
OAUTH_REMOTE_APP["signup_handler"]["info"] = "cds_ils.oauth:account_info"
OAUTHCLIENT_REMOTE_APPS = dict(cern_openid=OAUTH_REMOTE_APP)
###############################################################################
# REST
logout_redirect_url = os.environ.get("INVENIO_SPA_HOST", "https://127.0.0.1:3000/")
OAUTH_REMOTE_REST_APP = copy.deepcopy(cern_openid.REMOTE_REST_APP)
OAUTH_REMOTE_REST_APP["params"].update(_OAUTH_REMOTE_APP_COMMON)
OAUTH_REMOTE_REST_APP["signup_handler"]["info"] = "cds_ils.oauth:account_info_rest"
OAUTH_REMOTE_REST_APP["logout_url"] = os.environ.get(
    "OAUTH_CERN_OPENID_LOGOUT_URL",
    "https://keycloak-qa.cern.ch/auth/realms/cern/"
    "protocol/openid-connect/logout/?redirect_uri={}".format(logout_redirect_url),
)
OAUTH_REMOTE_REST_APP["authorized_redirect_url"] = (
    os.environ.get("INVENIO_SPA_HOST", "https://127.0.0.1:3000") + "/login"
)
OAUTH_REMOTE_REST_APP["disconnect_redirect_url"] = os.environ.get(
    "INVENIO_SPA_HOST", "https://127.0.0.1:3000"
)
OAUTH_REMOTE_REST_APP["error_redirect_url"] = (
    os.environ.get("INVENIO_SPA_HOST", "https://127.0.0.1:3000") + "/login"
)

OAUTHCLIENT_REST_REMOTE_APPS = dict(cern_openid=OAUTH_REMOTE_REST_APP)

###############################################################################
# Flask-Security
###############################################################################
# Disable user registration
SECURITY_REGISTERABLE = False
SECURITY_RECOVERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_CHANGEABLE = False
PERMANENT_SESSION_LIFETIME = timedelta(1)
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_POST_LOGOUT_VIEW = "/api/cern_openid/logout/"
# Override login template to remove local logins
# Use this in deployed envs, when having login via CERN SSO only
# OAUTHCLIENT_LOGIN_USER_TEMPLATE = "cds_ils/login_user.html"

###############################################################################
# OAI-PMH
###############################################################################
OAISERVER_ID_PREFIX = "oai:cds-ils:"

###############################################################################
# Migrator configuration
###############################################################################
MIGRATOR_RECORDS_DUMPLOADER_CLS = "cds_ils.migrator.records:CDSDocumentDumpLoader"
MIGRATOR_RECORDS_DUMP_CLS = "cds_ils.migrator.records:CDSRecordDump"

###############################################################################
# JSONSchemas
###############################################################################
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = "cds-ils.cern.ch"

# whitelist schemas for migration
JSONSCHEMAS_SCHEMAS = [
    "acquisition",
    "document_requests",
    "documents",
    "eitems",
    "ill",
    "internal_locations",
    "items",
    "invenio_opendefinition",
    "invenio_records_files",
    "loans",
    "locations",
    "providers",
    "series",
    "vocabularies",
]

###############################################################################
# RECORDS REST
###############################################################################
RECORDS_REST_ENDPOINTS[PATRON_PID_TYPE]["record_class"] = Patron
RECORDS_REST_ENDPOINTS[PATRON_PID_TYPE]["indexer_class"] = PatronIndexer
RECORDS_REST_ENDPOINTS[LOCATION_PID_TYPE]["create_permission_factory_imp"] = deny_all
RECORDS_REST_ENDPOINTS[LOCATION_PID_TYPE]["delete_permission_factory_imp"] = deny_all
# Override serializer for e-items that require authentication
RECORDS_REST_ENDPOINTS[DOCUMENT_PID_TYPE]["record_serializers"] = {
    "application/json": "cds_ils.literature.serializers:json_v1_response"
}
RECORDS_REST_ENDPOINTS[DOCUMENT_PID_TYPE]["search_serializers"] = {
    "application/json": "cds_ils.literature.serializers:json_v1_search",
    "text/csv": "cds_ils.literature.serializers:csv_v1_search",
}
RECORDS_REST_ENDPOINTS[DOCUMENT_PID_TYPE]["search_query_parser"] = query_params_modifier
RECORDS_REST_ENDPOINTS[EITEM_PID_TYPE]["record_serializers"] = {
    "application/json": "cds_ils.eitems.serializers:json_v1_response"
}
RECORDS_REST_ENDPOINTS[EITEM_PID_TYPE]["search_serializers"] = {
    "application/json": "cds_ils.eitems.serializers:json_v1_search",
    "text/csv": "cds_ils.eitems.serializers:csv_v1_search",
}
RECORDS_REST_ENDPOINTS[LITERATURE_PID_TYPE]["record_serializers"] = {
    "application/json": "invenio_app_ils.literature.serializers" ":json_v1_response"
}
RECORDS_REST_ENDPOINTS[LITERATURE_PID_TYPE]["search_serializers"] = {
    "application/json": "cds_ils.literature.serializers:json_v1_search",
    "text/csv": "cds_ils.literature.serializers:csv_v1_search",
}
RECORDS_REST_ENDPOINTS[LITERATURE_PID_TYPE][
    "search_query_parser"
] = query_params_modifier
RECORDS_REST_ENDPOINTS[SERIES_PID_TYPE]["record_serializers"] = {
    "application/json": "cds_ils.series.serializers" ":json_v1_response"
}
RECORDS_REST_ENDPOINTS[SERIES_PID_TYPE]["search_serializers"] = {
    "application/json": "cds_ils.series.serializers:json_v1_search",
    "text/csv": "cds_ils.series.serializers:csv_v1_search",
}
RECORDS_REST_ENDPOINTS[SERIES_PID_TYPE]["search_query_parser"] = query_params_modifier
RECORDS_REST_ENDPOINTS[ITEM_PID_TYPE]["record_loaders"] = {
    "application/json": "cds_ils.items.loaders:item_loader"
}
RECORDS_REST_ENDPOINTS[ITEM_PID_TYPE][
    "list_permission_factory_imp"
] = authenticated_user_permission
ILS_CIRCULATION_RECORDS_REST_ENDPOINTS[CIRCULATION_LOAN_PID_TYPE]["search_serializers"][
    "text/csv"
] = "cds_ils.circulation.serializers:csv_v1_search"
ILS_CIRCULATION_RECORDS_REST_ENDPOINTS[CIRCULATION_LOAN_PID_TYPE][
    "update_permission_factory_imp"
] = loan_checkout_permission

# show more tags in the facets
RECORDS_REST_FACETS["documents"]["aggs"]["tag"] = dict(
    terms=dict(field="tags", size=10)
)

###############################################################################
# ILS overridden
###############################################################################
ILS_VIEWS_PERMISSIONS_FACTORY = views_permissions_factory

ILS_LITERATURE_COVER_URLS_BUILDER = build_cover_urls

#: Period of time in days, before loans expire, for notifications etc.
ILS_CIRCULATION_LOAN_WILL_EXPIRE_DAYS = 3

#: Notification email for overdue loan sent automatically every X days
ILS_CIRCULATION_NOTIFICATION_OVERDUE_REMINDER_INTERVAL = 7

#: The maximum duration of a loan request
ILS_CIRCULATION_LOAN_REQUEST_DURATION_DAYS = 120
#: The minimum number of days after which a loan can start from the date of request
ILS_CIRCULATION_LOAN_REQUEST_OFFSET = 2

# Namespaces for fields added to the metadata schema
ILS_RECORDS_METADATA_NAMESPACES = {
    "document": {
        "unit": {"@context": "https://cern.ch/unit/terms"},
        "standard_review": {"@context": "https://cern.ch/standard_review/terms"},
    }
}

# Fields added to the metadata schema.
ILS_RECORDS_METADATA_EXTENSIONS = {
    "document": {
        "schema": Document._schema,
        "fields": {
            "unit_accelerator": {
                "elasticsearch": "keyword",
                "marshmallow": SanitizedUnicode(),
            },
            "unit_experiment": {
                "elasticsearch": "keyword",
                "marshmallow": List(SanitizedUnicode()),
            },
            "unit_institution": {
                "elasticsearch": "keyword",
                "marshmallow": List(SanitizedUnicode()),
            },
            "unit_project": {
                "elasticsearch": "keyword",
                "marshmallow": List(SanitizedUnicode()),
            },
            "unit_study": {
                "elasticsearch": "keyword",
                "marshmallow": List(SanitizedUnicode()),
            },
            "standard_review_applicability": {
                "elasticsearch": "keyword",
                "marshmallow": List(SanitizedUnicode()),
            },
            "standard_review_standard_validity": {
                "elasticsearch": "keyword",
                "marshmallow": SanitizedUnicode(),
            },
            "standard_review_checkdate": {
                "elasticsearch": "date",
                "marshmallow": SanitizedUnicode(),
            },
            "standard_review_comment": {
                "elasticsearch": "text",
                "marshmallow": SanitizedUnicode(),
            },
            "standard_review_expert": {
                "elasticsearch": "keyword",
                "marshmallow": SanitizedUnicode(),
            },
        },
    },
}

ILS_NOTIFICATIONS_TEMPLATES_CIRCULATION = {
    "bulk_extend": "cds_bulk_extend.html",
    "cancel": "cds_cancel.html",
    "request": "cds_request.html",
    "request_no_items": "cds_request_no_items.html",
    "checkin": "cds_checkin.html",
    "checkout": "cds_checkout.html",
    "self_checkout": "cds_self_checkout.html",
    "extend": "cds_extend.html",
    "overdue_reminder": "cds_overdue_reminder.html",
    "expiring_reminder": "cds_will_expire_in_reminder.html",
}

ILS_NOTIFICATIONS_TEMPLATES_DOCUMENT_REQUEST = {
    "request_accepted": "cds_document_request_accept.html",
    "request_declined_user_cancel": "cds_document_request_decline_user_cancel.html",  # noqa
    "request_declined_in_catalog": "cds_document_request_decline_in_catalog.html",  # noqa
    "request_declined_not_found": "cds_document_request_decline_not_found.html",  # noqa
    "request_declined_other": "cds_document_request_decline_other.html",
}

ILS_ILL_NOTIFICATIONS_TEMPLATES = {
    "extension_accepted": "cds_patron_loan_extension_accept.html",
    "extension_declined": "cds_patron_loan_extension_decline.html",
    "extension_requested": "cds_patron_loan_extension_request.html",
}

ILS_NOTIFICATIONS_TEMPLATES = {"footer": "cds_footer.html"}

# List of available vocabularies
ILS_VOCABULARIES = [
    "acq_medium",
    "acq_order_line_payment_mode",
    "acq_order_line_purchase_type",
    "acq_payment_mode",
    "acq_recipient",
    "affiliation_identifier_scheme",
    "alternative_identifier_scheme",
    "alternative_title_type",
    "author_identifier_scheme",
    "author_role",
    "author_type",
    "conference_identifier_scheme",
    "country",
    "currencies",
    "doc_req_type",
    "doc_req_payment_method",
    "doc_identifiers_materials",
    "doc_req_medium",
    "document_institutions",
    "document_standard_reviews",
    "doc_subjects",
    "eitem_sources",
    "identifier_scheme",
    "ill_item_type",
    "ill_payment_mode",
    "item_medium",
    "language",
    "license",
    "provider_type",
    "series_identifier_scheme",
    "series_url_access_restriction",
    "tag",
    "item_identifier_scheme",
    "shelf_number",
]

###############################################################################
# CIRCULATION overridden config
###############################################################################

CIRCULATION_POLICIES = dict(
    checkout=dict(
        duration_default=circulation_default_loan_duration,
        duration_validate=circulation_is_loan_duration_valid,
        item_can_circulate=can_item_circulate,
    ),
    extension=dict(
        from_end_date=True,
        duration_default=circulation_default_extension_duration,
        max_count=circulation_cds_extension_max_count,
    ),
    request=dict(can_be_requested=circulation_can_be_requested),
    upcoming_return_range=circulation_loan_will_expire_days,
)

CIRCULATION_LOAN_TRANSITIONS = {
    "CREATED": [
        dict(
            dest="PENDING",
            trigger="request",
            transition=CreatedToPending,
            permission_factory=authenticated_user_permission,
            assign_item=False,
        ),
        dict(
            dest="ITEM_ON_LOAN",
            trigger="checkout",
            transition=ILSToItemOnLoan,
            permission_factory=loan_checkout_permission,
        ),
        dict(
            dest="ITEM_ON_LOAN",
            trigger="self_checkout",
            transition=ILSToItemOnLoan,
            permission_factory=authenticated_user_permission,
        ),
    ],
    "PENDING": [
        dict(
            dest="ITEM_ON_LOAN",
            trigger="checkout",
            transition=ILSToItemOnLoan,
            permission_factory=backoffice_permission,
        ),
        dict(
            dest="ITEM_ON_LOAN",
            trigger="self_checkout",
            transition=ILSToItemOnLoan,
            permission_factory=authenticated_user_permission,
        ),
        dict(
            dest="CANCELLED",
            trigger="cancel",
            transition=ToCancelled,
            permission_factory=patron_owner_permission,
        ),
    ],
    "ITEM_ON_LOAN": [
        dict(
            dest="ITEM_RETURNED",
            trigger="checkin",
            transition=ItemOnLoanToItemReturned,
            permission_factory=backoffice_permission,
            assign_item=False,
        ),
        dict(
            dest="ITEM_ON_LOAN",
            transition=ILSItemOnLoanToItemOnLoan,
            trigger="extend",
            permission_factory=loan_extend_circulation_permission,
        ),
        dict(
            dest="CANCELLED",
            trigger="cancel",
            transition=ToCancelled,
            permission_factory=backoffice_permission,
        ),
    ],
    "ITEM_RETURNED": [],
    "CANCELLED": [],
}

ILS_PATRON_ANONYMOUS_CLASS = AnonymousPatron

###############################################################################
# CDS-ILS configuration
###############################################################################
#: LDAP configuration
CDS_ILS_LDAP_URL = "ldap://xldap.cern.ch"
#: number of checks (synchronisations) before user deletion
CDS_ILS_PATRON_DELETION_CHECKS = 30
#: Literature covers Syndetic client ID
CDS_ILS_SYNDETIC_CLIENT = "CHANGE_ME"
#: EzProxy URL
CDS_ILS_EZPROXY_URL = "https://ezproxy.cern.ch/login?url={url}"
# Eitem DOI URL prefix
CDS_ILS_DOI_URL_PREFIX = "http://dx.doi.org/{doi}"

###############################################################################
# CDS-ILS importer configuration
###############################################################################

CDS_ILS_IMPORTER_RECORD_TAG = "//*[local-name() = 'record']"

CDS_ILS_IMPORTER_PROVIDERS = {
    "cds": {
        "priority": 1,
        "agency_code": "SzGeCERN",
    },
    "snv": {
        "priority": 3,
        "agency_code": "SNV",
    },
    "springer": {
        "priority": 2,
        "agency_code": "DE-He213",
    },
    "oso": {
        "priority": 3,
        "agency_code": "StDuBDS",
    },
    "ams": {
        "priority": 3,
        "agency_code": "RPAM",
    },
    "cbo": {
        "priority": 3,
        "agency_code": "UkCbUP",
    },
    "ieee": {
        "priority": 3,
        "agency_code": "IEEE",
    },
    "wsc": {
        "priority": 3,
        "agency_code": "WSP",
    },
    "iop": {
        "priority": 3,
        "agency_code": "IOP",
    },
    "gru": {
        "priority": 3,
        "agency_code": "DE-B1597",
    },
    "taf": {
        "priority": 3,
        "agency_code": "FlBoTFG",
    },
    "wil": {
        "priority": 3,
        "agency_code": "JwS",
    },
    "elsevier": {
        "priority": 3,
        "agency_code": "OCLC-NEEBV",
    },
    "woodhead": {
        "priority": 3,
        "agency_code": "OCLC-UKWHP",
    },
    "iospress": {
        "priority": 3,
        "agency_code": "OCLC-B91",
    },
    "mitpress": {
        "priority": 3,
        "agency_code": "MaCbMITP",
    },
    "ebl": {"priority": 4, "agency_code": "MiAaPQ"},
    "safari": {"priority": 4, "agency_code": "OCoLC"},
}

CDS_ILS_IMPORTER_UPLOADS_PATH = "/tmp"

CDS_ILS_IMPORTER_FILE_EXTENSIONS_ALLOWED = [".xml"]

CDS_ILS_IMPORTER_PROVIDERS_ALLOWED_TO_DELETE_RECORDS = ["ebl", "safari", "cds"]

CDS_ILS_RECORD_LEGACY_PID_TYPE = "ldocid"
CDS_ILS_SERIES_LEGACY_PID_TYPE = "lserid"
CDS_ILS_BORROWING_REQ_LEGACY_PID_TYPE = "lillid"
CDS_ILS_ACQ_ORDER_LEGACY_PID_TYPE = "lacqid"
CDS_ILS_ITEM_LEGACY_PID_TYPE = "lpitid"
CDS_ILS_LOAN_LEGACY_PID_TYPE = "lloaid"

CDS_ILS_INDEX_LOCAL_ACCOUNTS = True

CDS_ILS_MIGRATION_ALLOW_UPDATES = False
CDS_ILS_MIGRATION_FILES_DIR = "/eos/media/cds/test/books/migration/"

ILS_ILL_NOTIFICATIONS_FILTER = ill_notifications_filter
ILS_NOTIFICATIONS_FILTER_DOCUMENT_REQUEST = document_requests_notifications_filter
SECURITY_PASSWORD_SINGLE_HASH = True

# Feature Toggles
ILS_SELF_CHECKOUT_ENABLED = True

REST_CSRF_ENABLED = False

###############################################################################
# CORS
###############################################################################
REST_ENABLE_CORS = True
CORS_SEND_WILDCARD = False
CORS_SUPPORTS_CREDENTIALS = True
