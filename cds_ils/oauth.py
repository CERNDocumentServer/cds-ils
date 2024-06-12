# Copyright (C) 2024 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS oauth overrides."""
from flask import current_app, flash, g, redirect
from invenio_oauthclient.contrib.cern_openid import get_resource
from invenio_oauthclient.errors import OAuthCERNRejectedAccountError
from invenio_oauthclient.handlers.rest import response_handler


def _account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    g.oauth_logged_in_with_remote = remote
    resource = get_resource(remote, resp)

    valid_roles = current_app.config.get("OAUTHCLIENT_CERN_OPENID_ALLOWED_ROLES")
    cern_roles = resource.get("cern_roles")
    if cern_roles is None or not set(cern_roles).issubset(valid_roles):
        raise OAuthCERNRejectedAccountError(
            "User roles {0} are not one of {1}".format(cern_roles, valid_roles),
            remote,
            resp,
        )

    email = resource["email"]
    external_id = resource["cern_upn"]
    nice = resource["preferred_username"]
    name = "{0}, {1}".format(resource["family_name"].upper(), resource["given_name"])

    return dict(
        user=dict(email=email.lower(), profile=dict(username=nice, full_name=name)),
        external_id=external_id,
        external_method="cern_openid",
        active=True,
    )


def account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    try:
        return _account_info(remote, resp)
    except OAuthCERNRejectedAccountError as e:
        current_app.logger.warning(e.message, exc_info=True)
        flash(_("CERN account not allowed."), category="danger")
        return redirect("/")


def account_info_rest(remote, resp):
    """Retrieve remote account information used to find local user."""
    try:
        return _account_info(remote, resp)
    except OAuthCERNRejectedAccountError as e:
        current_app.logger.warning(e.message, exc_info=True)
        remote_app_config = current_app.config["OAUTHCLIENT_REST_REMOTE_APPS"][
            remote.name
        ]
        return response_handler(
            remote,
            remote_app_config["error_redirect_url"],
            payload=dict(message="CERN account not allowed.", code=400),
        )
