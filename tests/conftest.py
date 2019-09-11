# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# CDS Books is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Common pytest fixtures and plugins."""

from __future__ import absolute_import, print_function

import pytest
from invenio_accounts.models import User
from invenio_oauthclient.models import RemoteAccount, UserIdentity
from invenio_userprofiles.models import UserProfile


@pytest.fixture()
def system_user(app, db):
    """Create a regular system user."""
    user = User(**dict(email="system_user@cern.ch", active=True))
    db.session.add(user)
    db.session.commit()

    user_id = user.id

    identity = UserIdentity(**dict(
        id="1", method="cern", id_user=user_id
    ))
    db.session.add(identity)

    profile = UserProfile(**dict(
        user_id=user_id, _displayname="id_" + str(user_id),
        full_name="System User"
    ))
    db.session.add(profile)

    remote_account = RemoteAccount(
                        client_id="CLIENT_ID",
                        **dict(
                            user_id=user_id,
                            extra_data=dict(
                                person_id="1",
                                department="Department"
                            )
                        )
                    )
    db.session.add(remote_account)
    db.session.commit()
    return user
