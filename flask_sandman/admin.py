"""This module contains the custom admin class that allows for a nicer admin interface."""
# Functools
from functools import partial
# Package resources
import pkg_resources
# Flask: Administration
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# Sandman
from .database import DATABASE as db

class AdminView(ModelView):  # pylint: disable=no-init
    """Define custom templates for each view."""
    list_template = 'list.html'
    create_template = 'create.html'
    edit_template = 'edit.html'
    column_display_pk = True


administration = partial(Admin, base_template='layout.html', template_mode='bootstrap3') # base_template defaults to bootstrap(2|3)/admin/base.html in Flask-Admin

def register(router, model, database = db, view = AdminView):
    """Register an administration view for each model

    :param app: Flaks application
    :param list models: A list of AutomapModels
    :param Admin router: An instance of Flask's Admin
    :param ModelView view:
    :return:
    """
    if hasattr(model, "__admin__") and model.__admin__:
        admin_view = model.__admin__(database.session) # TODO : Experimental : This allows users to provide their own admin views upon custom models
    else:
        admin_view = view(model, database.session)
    router.add_view(admin_view)
    return admin_view
