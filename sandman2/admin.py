"""This module contains the custom admin class that allows for a nicer admin
interface."""

# pylint: disable=maybe-no-member,too-few-public-methods

# Third-party imports
from flask_admin.contrib.sqla import ModelView

class CustomAdminView(ModelView):  # pylint: disable=no-init
    """Define custom templates for each view."""
    list_template = 'list.html'
    create_template = 'create.html'
    edit_template = 'edit.html'
    column_display_pk = True
