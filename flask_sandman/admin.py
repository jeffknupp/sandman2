"""This module contains the custom admin class that allows for a nicer admin
interface."""

# pylint: disable=maybe-no-member,too-few-public-methods

# Third-party imports
from flask_admin.contrib.sqla import ModelView

# Application imports
from .database import DATABASE as db

class AdminView(ModelView):  # pylint: disable=no-init
    """Define custom templates for each view."""
    list_template = 'list.html'
    create_template = 'create.html'
    edit_template = 'edit.html'
    column_display_pk = True


def register(router, model, database = db, admin_view = AdminView):
    """Register an administration view for each model

    :param app: Flaks application
    :param list models: A list of AutomapModels
    :param Admin router: An instance of Flask's Admin
    :param ModelView admin_view:
    :return:
    """
    if hasattr(model, "__admin__") and model.__admin__:
        view = model.__admin__(database.session) # TODO : Experimental : This allows users to provide their own admin views upon custom models
    else:
        view = admin_view(model, database.session)
    router.add_view(view)
    return view

