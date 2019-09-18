"""Sandman2 main application setup code."""

# Third-party imports
from flask import Flask, current_app, jsonify
from sqlalchemy.sql import sqltypes

# Application imports
from flask_sandman.exception import register as register_exceptions
from flask_sandman.service import Service, register as register_service
from flask_sandman.database import DATABASE as db
from flask_sandman.model import Model, AutomapModel, register as register_model
from flask_sandman.admin import register as register_admin_view
from flask_admin import Admin
from flask_httpauth import HTTPBasicAuth

# Augment flask_sandman's Model class with the Automap and Flask-SQLAlchemy model
# classes
auth = HTTPBasicAuth()

def get_app(
        database_uri,
        exclude_tables=None,
        user_models=None,
        reflect_all=True,
        read_only=False,
        schema=None):
    """Return an application instance connected to the database described in
    *database_uri*.

    :param str database_uri: The URI connection string for the database
    :param list exclude_tables: A list of tables to exclude from the API
                                service
    :param list user_models: A list of user-defined models to include in the
                             API service
    :param bool reflect_all: Include all database tables in the API service
    :param bool read_only: Only allow HTTP GET commands for all endpoints
    :param str schema: Use the specified named schema instead of the default
    """
    app = Flask('flask_sandman')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SANDMAN2_READ_ONLY'] = read_only
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.classes = []
    db.init_app(app)
    admin = Admin(app, base_template='layout.html', template_mode='bootstrap3')
    register_exceptions(app)
    if user_models:
        with app.app_context():
            _register_user_models(user_models, admin, schema=schema)
    elif reflect_all:
        with app.app_context():
            _reflect_all(exclude_tables, admin, read_only, schema=schema)

    @app.route('/')
    def index():
        """Return a list of routes to the registered classes."""
        routes = {}
        for cls in app.classes:
            routes[cls.__model__.__name__] = '{}{{/{}}}'.format(
                cls.__model__.__url__,
                cls.__model__.primary_key())
        return jsonify(routes)
    return app


def _register_user_models(user_models, admin=None, schema=None):
    """Register any user-defined models with the API Service.

    :param list user_models: A list of user-defined models to include in the
                             API service
    """
    if any([issubclass(cls, AutomapModel) for cls in user_models]):
        AutomapModel.prepare(  # pylint:disable=maybe-no-member
                               db.engine, reflect=True, schema=schema)

    for user_model in user_models:
        register_model(user_model, admin)


def _reflect_all(exclude_tables=None, admin=None, read_only=False, schema=None):
    """Register all tables in the given database as services.

    :param list exclude_tables: A list of tables to exclude from the API
                                service
    """
    AutomapModel.prepare(  # pylint:disable=maybe-no-member
        db.engine, reflect=True, schema=schema)
    for cls in AutomapModel.classes:
        if exclude_tables and cls.__table__.name in exclude_tables:
            continue
        if read_only:
            cls.__methods__ = {'GET'}
        register_model(cls, admin)


