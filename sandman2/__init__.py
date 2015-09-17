"""*sandman2*'s main module."""

# Third-party imports
from flask import Flask, current_app, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base

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
from sandman2.model import db, Model
from sandman2.admin import CustomAdminView
from flask.ext.admin import Admin

__version__ = '0.0.6'

# Augment sandman2's Model class with the Automap and Flask-SQLAlchemy model
# classes
Model = declarative_base(cls=(Model, db.Model))
AutomapModel = automap_base(Model)


def get_app(
        database_uri,
        exclude_tables=None,
        user_models=None,
        reflect_all=True):
    """Return an application instance connected to the database described in
    *database_uri*.

    :param str database_uri: The URI connection string for the database
    :param list exclude_tables: A list of tables to exclude from the API
                                service
    :param list user_models: A list of user-defined models to include in the
                             API service
    :param bool reflect_all: Include all database tables in the API service
    """
    app = Flask('sandman2')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.init_app(app)
    admin = Admin(app, base_template='layout.html')
    _register_error_handlers(app)
    if user_models:
        with app.app_context():
            _register_user_models(user_models, admin)
    elif reflect_all:
        with app.app_context():
            _reflect_all(exclude_tables, admin)
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


def register_service(cls, primary_key_type='int'):
    """Register an API service endpoint.

    :param cls: The class to register
    :param str primary_key_type: The type (as a string) of the primary_key
                                 field
    """
    view_func = cls.as_view(cls.__name__.lower())  # pylint: disable=no-member
    methods = set(cls.__model__.__methods__)  # pylint: disable=no-member

    if 'GET' in methods:  # pylint: disable=no-member
        current_app.add_url_rule(
            cls.__model__.__url__, defaults={'resource_id': None},
            view_func=view_func,
            methods=['GET'])
        current_app.add_url_rule(
            '{resource}/meta'.format(resource=cls.__model__.__url__),
            view_func=view_func,
            methods=['GET'])
    if 'POST' in methods:  # pylint: disable=no-member
        current_app.add_url_rule(
            cls.__model__.__url__, view_func=view_func, methods=['POST', ])
    current_app.add_url_rule(
        '{resource}/<{pk_type}:{pk}>'.format(
            resource=cls.__model__.__url__,
            pk='resource_id', pk_type=primary_key_type),
        view_func=view_func,
        methods=methods - set(['POST']))


def _reflect_all(exclude_tables=None, admin=None):
    """Register all tables in the given database as services.

    :param list exclude_tables: A list of tables to exclude from the API
                                service
    """
    AutomapModel.prepare(  # pylint:disable=maybe-no-member
        db.engine, reflect=True)
    for cls in AutomapModel.classes:
        if exclude_tables and cls.__table__.name in exclude_tables:
            continue
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
            '__version__': __version__,
        })
    register_service(service_class)
    if admin is not None:
        admin.add_view(CustomAdminView(cls, db.session))


def _register_user_models(user_models, admin=None):
    """Register any user-defined models with the API Service.

    :param list user_models: A list of user-defined models to include in the
                             API service
    """
    if any([True for cls in user_models if issubclass(cls, AutomapModel)]):
        AutomapModel.prepare(  # pylint:disable=maybe-no-member
                               db.engine, reflect=True)

    for user_model in user_models:
        if not issubclass(user_model, AutomapModel):
            model_type = type(user_model.__name__, (user_model, Model), {})
            register_model(model_type, admin)
        else:
            register_model(user_model, admin)
