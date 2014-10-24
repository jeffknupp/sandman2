"""This module contains the custom admin class that allows for a nicer admin
interface."""

# pylint: disable=maybe-no-member,too-few-public-methods

# Third-party imports
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin


admin = Admin(base_template='layout.html')


class CustomAdminView(ModelView):  # pylint: disable=no-init
    """Define custom templates for each view."""
    list_template = 'list.html'
    create_template = 'create.html'
    edit_template = 'edit.html'
