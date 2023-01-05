# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS authentication views module."""

from flask import Blueprint, current_app, redirect

cern_oauth_blueprint = Blueprint("cern_openid_oauth", __name__)


@cern_oauth_blueprint.route("/cern_openid/logout/")
def logout_redirect():
    """Redirect to the CERN OpenID logout."""
    return redirect(current_app.config["OAUTH_REMOTE_REST_APP"]["logout_url"])
