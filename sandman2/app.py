"""Sandman2 main application setup code."""

# Third-party imports
from flask import Flask, current_app, jsonify
from sqlalchemy.sql import sqltypes

# Application imports
from sandman2.exception import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    NotAcceptableException,
    NotImplementedException,
    ConflictException,
    ServerErrorException,
    ServiceUnavailableException,
    )
from sandman2.service import Service
from sandman2.model import db, Model, AutomapModel
from sandman2.admin import CustomAdminView
from flask_admin import Admin
from flask_httpauth import HTTPBasicAuth

# Augment sandman2's Model class with the Automap and Flask-SQLAlchemy model
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
    app = Flask('sandman2')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SANDMAN2_READ_ONLY'] = read_only
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.classes = []
    db.init_app(app)
    admin = Admin(app, base_template='layout.html', template_mode='bootstrap3')
    _register_error_handlers(app)
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


def _register_error_handlers(app):
    """Register error-handlers for the application.

    :param app: The application instance
    """
    @app.errorhandler(BadRequestException)
    @app.errorhandler(ForbiddenException)
    @app.errorhandler(NotAcceptableException)
    @app.errorhandler(NotFoundException)
    @app.errorhandler(ConflictException)
    @app.errorhandler(ServerErrorException)
    @app.errorhandler(NotImplementedException)
    @app.errorhandler(ServiceUnavailableException)
    def handle_application_error(error):  # pylint:disable=unused-variable
        """Handler used to send JSON error messages rather than default HTML
        ones."""
        response = jsonify(error.to_dict())
        response.status_code = error.code
        return response


def register_service(cls, primary_key_type):
    """Register an API service endpoint.

    :param cls: The class to register
    :param str primary_key_type: The type (as a string) of the primary_key
                                 field
    """
    view_func = cls.as_view(cls.__name__.lower())  # pylint: disable=no-member
    methods = set(cls.__model__.__methods__)  # pylint: disable=no-member

    if 'GET' in methods:  # pylint: disable=no-member
        current_app.add_url_rule(
            cls.__model__.__url__ + '/', defaults={'resource_id': None},
            view_func=view_func,
            methods=['GET'])
        current_app.add_url_rule(
            '{resource}/meta'.format(resource=cls.__model__.__url__),
            view_func=view_func,
            methods=['GET'])
    if 'POST' in methods:  # pylint: disable=no-member
        current_app.add_url_rule(
            cls.__model__.__url__ + '/', view_func=view_func, methods=['POST', ])
    current_app.add_url_rule(
        '{resource}/<{pk_type}:{pk}>'.format(
            resource=cls.__model__.__url__,
            pk='resource_id', pk_type=primary_key_type),
        view_func=view_func,
        methods=methods - {'POST'})
    current_app.classes.append(cls)


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


def register_model(cls, admin=None):
    """Register *cls* to be included in the API service

    :param cls: Class deriving from :class:`sandman2.models.Model`
    """
    cls.__url__ = '/{}'.format(cls.__name__.lower())
    service_class = type(
        cls.__name__ + 'Service',
        (Service,),
        {
            '__model__': cls,
        })

    # inspect primary key
    cols = list(cls().__table__.primary_key.columns)

    # composite keys not supported (yet)
    primary_key_type = 'string'
    if len(cols) == 1:
        col_type = cols[0].type
        # types defined at http://flask.pocoo.org/docs/0.10/api/#url-route-registrations
        if isinstance(col_type, sqltypes.String):
            primary_key_type = 'string'
        elif isinstance(col_type, sqltypes.Integer):
            primary_key_type = 'int'
        elif isinstance(col_type, sqltypes.Numeric):
            primary_key_type = 'float'

    # registration
    register_service(service_class, primary_key_type)
    if admin is not None:
        admin.add_view(CustomAdminView(cls, db.session))


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
