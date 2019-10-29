"""Automatically generated REST API services from SQLAlchemy
ORM models or a database introspection.

.. note ::

    I haven't worked out how to determine the application type on the fly and am currently storing this within the application configuration
"""
# Third-party imports
import flask
from flask import current_app, request, make_response
from flask.views import MethodView
from sqlalchemy import asc, desc

# Application imports
from flask_sandman.exception import NotFoundException, BadRequestException
from flask_sandman.database import DATABASE as db
from flask_sandman.decorators import etag, validate_fields


def add_link_headers(response, links):
    """Return *response* with the proper link headers set, based on the contents
    of *links*.

    :param response: :class:`flask.Response` response object for links to be
                     added
    :param dict links: Dictionary of links to be added
    :rtype :class:`flask.Response` :
    """
    link_string = '<{}>; rel=self'.format(links['self'])
    for link in links.values():
        link_string += ', <{}>; rel=related'.format(link)
    response.headers['Link'] = link_string
    return response


def jsonify(resource):
    """Return a Flask ``Response`` object containing a
    JSON representation of *resource*.

    :param resource: The resource to act as the basis of the response
    """

    response = flask.jsonify(resource.to_dict())
    response = add_link_headers(response, resource.links())
    return response


def is_valid_method(model, resource=None):
    """:class:`Service` classes may define an :meth:`is_valid_get|post|put|delete` method.

    Such methods receive the current request and possibly a record as their arguments returning a relevant error message to be sent to the client"""
    validation_function_name = 'is_valid_{}'.format(
        request.method.lower())
    if hasattr(model, validation_function_name):
        return getattr(model, validation_function_name)(request, resource)

class Service(MethodView):

    """The *Service* class is a generic extension of Flask's *MethodView*,
    providing default RESTful functionality for a given ORM resource.

    Each service has an associated *__model__* attribute which represents the
    ORM resource it exposes. Services are JSON-only. HTML-based representation
    is available through the admin interface.
    """

    #: The flask_sandman.model.Model-derived class to expose
    __model__ = None

    #: The string used to describe the elements when a collection is
    #: returned.
    __json_collection_name__ = 'resources' # None #  TODO : Make this None by default

    def delete(self, resource_id):
        """Return an HTTP response object resulting from a HTTP DELETE call.

        :param resource_id: The value of the resource's primary key
        """
        resource = self._resource(resource_id)
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        db.session().delete(resource)
        db.session().commit()
        return self._no_content_response()

    @etag
    def get(self, resource_id=None):
        """Return an HTTP response object resulting from an HTTP GET call.

        If *resource_id* is provided, return just the single resource.
        Otherwise, return the full collection.

        :param resource_id: The value of the resource's primary key
        """
        if request.path.endswith('meta'): # Change to '.meta'
            return self._meta()
        #if request.path.endswith('.csv'):
        #    return self.csv(self._all_resources())

        if resource_id is None:
            error_message = is_valid_method(self.__model__)
            if error_message:
                raise BadRequestException(error_message)
            # Handled by the CSV endpoint
            if 'export' in request.args: 
                return self.csv(self._all_resources())
            # return self.records2JSON({self.__json_collection_name__: self._all_resources()} if self.__json_collection_name__ else self._all_resources())
            return flask.jsonify({self.__json_collection_name__: self._all_resources()})
        else:
            resource = self._resource(resource_id)
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            return self.record2JSON(resource)

    def patch(self, resource_id):
        """Return an HTTP response object resulting from an HTTP PATCH call.

        :returns: ``HTTP 200`` if the resource already exists
        :returns: ``HTTP 400`` if the request is malformed
        :returns: ``HTTP 404`` if the resource is not found
        :param resource_id: The value of the resource's primary key
        """
        resource = self._resource(resource_id)
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        if not request.json:
            raise BadRequestException('No JSON data received')
        resource.update(request.json)
        db.session().merge(resource)
        db.session().commit()
        return self.record2JSON(resource)

    @validate_fields
    def post(self):
        """Return the JSON representation of a new resource created through
        an HTTP POST call.

        :returns: ``HTTP 201`` if a resource is properly created
        :returns: ``HTTP 204`` if the resource already exists
        :returns: ``HTTP 400`` if the request is malformed or missing data
        """
        resource = self.__model__.query.filter_by(**request.json).first()
        if resource:
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            return self._no_content_response()

        resource = self.__model__(**request.json)  # pylint: disable=not-callable
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        db.session().add(resource)
        db.session().commit()
        return self._created_response(resource)

    def put(self, resource_id):
        """Return the JSON representation of a new resource created or updated
        through an HTTP PUT call.

        If resource_id is not provided, it is assumed the primary key field is
        included and a totally new resource is created. Otherwise, the existing
        resource referred to by *resource_id* is updated with the provided JSON
        data. This method is idempotent.

        :returns: ``HTTP 201`` if a new resource is created
        :returns: ``HTTP 200`` if a resource is updated
        :returns: ``HTTP 400`` if the request is malformed or missing data
        """
        resource = self.__model__.query.get(resource_id)
        if resource:
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            resource.update(request.json)
            db.session().merge(resource)
            db.session().commit()
            return self.record2JSON(resource)

        resource = self.__model__(**request.json)  # pylint: disable=not-callable
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        db.session().add(resource)
        db.session().commit()
        return self._created_response(resource)

    def _meta(self): # TODO : Rename to __meta__ or meta
        """Return a description of this resource as reported by the
        database."""
        return flask.jsonify(self.__model__.description())

    def _resource(self, resource_id): # TODO : Rename to _record_ or recordByID
        """Return the ``flask_sandman.model.Model`` instance with the given
        *resource_id*.

        :rtype: :class:`sandman2.model.Model`
        """
        resource = self.__model__.query.get(resource_id)
        if not resource:
            raise NotFoundException()
        return resource

    def _all_resources(self): # TODO : Rename to _records_ or _collection_
        """Return the complete collection of resources as a list of
        dictionaries.

        :rtype: :class:`sandman2.model.Model`
        """
        queryset = self.__model__.query
        args = {k: v for (k, v) in request.args.items() if k not in ('page', 'export')}
        limit = None
        if args:
            filters = []
            order = []
            for key, value in args.items():
                if value.startswith('%'):
                    filters.append(getattr(self.__model__, key).like(str(value), escape='/'))
                elif key == 'sort':
                    direction = desc if value.startswith('-') else asc
                    order.append(direction(getattr(self.__model__, value.lstrip('-'))))
                elif key == 'limit':
                    limit = int(value)
                elif hasattr(self.__model__, key):
                    filters.append(getattr(self.__model__, key) == value)
                else:
                    raise BadRequestException('Invalid field [{}]'.format(key))
            queryset = queryset.filter(*filters).order_by(*order)
        if 'page' in request.args:
            resources = queryset.paginate(page=int(request.args['page']), per_page=limit).items
        else:
            queryset = queryset.limit(limit)
            resources = queryset.all()
        return [r.retrieve() for r in resources]

    def csv(self, collection):
        """Return a CSV of the resources in *collection*.

        :param list collection: A list of resources represented by dicts
        """
        fieldnames = collection[0].keys()
        faux_csv = ','.join(fieldnames) + '\r\n'
        for resource in collection:
            faux_csv += ','.join((str(x) for x in resource.values())) + '\r\n'
        response = make_response(faux_csv)
        response.mimetype = 'text/csv'
        return response

    @staticmethod
    def records2JSON(resources):
        """Return a collection of records

        .. todo::

            This should really accept a SQL query object rather then a list of dicts.
            It should also be integrated with `self.record2JSON`.

        :param resources: A list of dictioneries as determined by self._all_resources.
        :return: Either a `dict` or a `Response`
        """
        # if current_app.config.get("APP_TYPE", None) == FlaskAPI: # TODO : [1]
        #     return resources
        # else :
        return flask.jsonify(resources)

    @staticmethod
    def record2JSON(resource):
        """Return a Flask ``Response`` object containing a
        JSON representation of *resource*.

        :param resource: The resource to act as the basis of the response
        """
        # if current_app.config.get("APP_TYPE", None) == FlaskAPI: # TODO : [1]
        #     return resource.retrieve()
        # else :
        response = flask.jsonify(resource.retrieve())
        print(resource.links())
        response = add_link_headers(response, resource.links())
        return response

    @staticmethod
    def _no_content_response():
        """Return an HTTP 204 "No Content" response.

        :returns: HTTP Response
        """
        response = make_response()
        response.status_code = 204
        return response

    @staticmethod
    def _created_response(resource):
        """Return an HTTP 201 "Created" response.

        :returns: HTTP Response
        """
        response = Service.record2JSON(resource)
        response.status_code = 201
        return response

    # TODO : Override as_view to use the current models name/URL ?

# TODO : [1] Properly determine the application type; Presently users must store the application type in the application configuration e.g. app.config["app_type"] = type(app); Testing the attribute wsgi_app of current_app seems promising but this is a function not a reference to the application

def register(router, service, primary_key_type):
    """Register an API service endpoint.

    :param service: The class to register
    :param str primary_key_type: The type (as a string) of the primary_key
                                 field
    """
    view_func = service.as_view(service.__model__.__name__.lower()) # Originally : service.__name__.lower()) Currently : service.__model__.__url__
    methods = set(service.__model__.__methods__)  # pylint: disable=no-member
    resource = service.__model__.__url__.strip("/")

    if 'GET' in methods:  # pylint: disable=no-member
        router.add_url_rule('/{resource}/'.format(resource=resource),
                            defaults={'resource_id': None},
                            view_func=view_func,
                            methods=['GET'])
        router.add_url_rule('/{resource}.meta'.format(resource=resource),
                            view_func=view_func,
                            methods=['GET'])
    if 'POST' in methods:  # pylint: disable=no-member
        router.add_url_rule('/{resource}/'.format(resource=resource),
                            view_func=view_func,
                            methods=['POST', ])
    router.add_url_rule('/{resource}/<{pk_type}:{pk}>'.format(
            resource=resource,
            pk='resource_id',
            pk_type=primary_key_type),
        view_func=view_func,
        methods=methods - {'POST'})
    # current_app.classes.append(service)
