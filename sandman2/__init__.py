"""sandman2 is a RESTful API service generator for legacy databases."""

# Third-party imports
from flask import Flask, current_app, jsonify
from flask.ext.admin.contrib.sqla import ModelView
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
from sandman2.admin import admin, CustomAdminView

__version__ = '0.0'

SandmanModel = Model
Model = declarative_base(cls=(Model, db.Model))
AutomapModel = automap_base(Model)
_SERVICE_CLASSES = []


def get_app(database_uri):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.init_app(app)
    admin.init_app(app)
    _register_error_handlers(app)
    return app

def _register_error_handlers(app):
    """Register error-handlers for the application.

    :param app: the application instance
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
    _SERVICE_CLASSES.append(cls)
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


def reflect_all():
    AutomapModel.prepare(  # pylint:disable=maybe-no-member
        db.engine, reflect=True)
    for cls in AutomapModel.classes:
        cls.__url__ = '/{}'.format(cls.__name__.lower())
        ServiceClass = type(cls.__name__ + 'Service', (Service,),
                {
                    '__model__': cls,
                    '__version__': __version__,
                })
        register_service(ServiceClass)
        admin.add_view(CustomAdminView(cls, db.session))
