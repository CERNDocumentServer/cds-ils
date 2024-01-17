# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Admin panel for ldap synchronizations."""

import flask
from flask import Blueprint, current_app, flash, redirect, request
from flask_admin.base import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from invenio_i18n import gettext as _

from cds_ils.ldap.models import LdapSynchronizationLog
from cds_ils.ldap.tasks import synchronize_users_task


class LdapSynchronizationLogModelView(ModelView):
    """Invenio admin view for ldap users synchronization."""

    # Entries are read-only
    can_create = True
    can_edit = False
    can_delete = False

    can_view_details = True

    form_excluded_columns = LdapSynchronizationLog.__table__.columns
    column_default_sort = (LdapSynchronizationLog.start_time, True)

    @expose("/new/", methods=("GET", "POST"))
    def create_view(self):
        """Override the creation form and replace it by an action button."""
        if flask.request.method == "POST":
            try:
                self.start_task()
                flash("The task was successfully started.", "success")
            except Exception as e:
                current_app.logger.exception(e)
                flash("An error occurred while starting the task.", "error")
            return redirect(request.path)  # Redirect after POST

        return_url = get_redirect_target() or self.get_url(".index_view")

        return self.render("cds_ils_admin/create_task.html", return_url=return_url)

    @staticmethod
    def start_task():
        """Start the task as requested by the user."""
        synchronize_users_task.apply_async()


blueprint = Blueprint(
    "cds_ils_admin",
    __name__,
    template_folder="templates",
    static_folder="static",
)

ldap_sync = {
    "model": LdapSynchronizationLog,
    "modelview": LdapSynchronizationLogModelView,
    "name": "Ldap Synchronization",
    "category": _("User Management"),
}

__all__ = ("ldap_sync",)
