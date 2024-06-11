from flask import session, current_app, flash, redirect, g
from jwt import decode

from invenio_oauthclient.errors import OAuthCERNRejectedAccountError
from invenio_oauthclient.handlers.rest import response_handler


def get_dict_from_response(response):
    """Prepare new mapping with 'Value's grouped by 'Type'."""
    result = {}
    if getattr(response, "_resp") and response._resp.code > 400:
        return result

    for key, value in response.data.items():
        result.setdefault(key, value)
    return result


def get_resource(remote, token_response=None):
    """Query CERN Resources to get user info and roles."""
    cached_resource = session.pop("cern_resource", None)
    if cached_resource:
        return cached_resource

    url = current_app.config.get("OAUTHCLIENT_CERN_OPENID_USERINFO_URL")
    response = remote.get(url)
    dict_response = get_dict_from_response(response)
    if token_response:
        decoding_params = dict(
            options=dict(
                verify_signature=False,
                verify_aud=False,
            ),
            algorithms=["HS256", "RS256"],
        )
        token_data = decode(token_response["access_token"], **decoding_params)
        dict_response.update(token_data)
    session["cern_resource"] = dict_response
    return dict_response


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
