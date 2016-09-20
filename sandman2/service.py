"""Automatically generated REST API services from SQLAlchemy
ORM models or a database introspection."""

# Third-party imports
from flask import request, make_response
import flask
from flask.views import MethodView

# Application imports
from sandman2.exception import NotFoundException, BadRequestException
from sandman2.model import db
from sandman2.decorators import etag, validate_fields


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
    """Return the error message to be sent to the client if the current
    request passes fails any user-defined validation."""
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

    #: The sandman2.model.Model-derived class to expose
    __model__ = None

    #: The string used to describe the elements when a collection is
    #: returned.
    __json_collection_name__ = 'resources'

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
        if request.path.endswith('meta'):
            return self._meta()

        if resource_id is None:
            error_message = is_valid_method(self.__model__)
            if error_message:
                raise BadRequestException(error_message)

            if 'export' in request.args: 
                return self._export(self._all_resources())

            return flask.jsonify({
                self.__json_collection_name__: self._all_resources()
                })
        else:
            resource = self._resource(resource_id)
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            return jsonify(resource)

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
        return jsonify(resource)

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
            return jsonify(resource)

        resource = self.__model__(**request.json)  # pylint: disable=not-callable
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        db.session().add(resource)
        db.session().commit()
        return self._created_response(resource)

    def _meta(self):
        """Return a description of this resource as reported by the
        database."""
        return flask.jsonify(self.__model__.description())

    def _resource(self, resource_id):
        """Return the ``sandman2.model.Model`` instance with the given
        *resource_id*.

        :rtype: :class:`sandman2.model.Model`
        """
        resource = self.__model__.query.get(resource_id)
        if not resource:
            raise NotFoundException()
        return resource

    def _all_resources(self):
        """Return the complete collection of resources as a list of
        dictionaries.

        :rtype: :class:`sandman2.model.Model`
        """
        queryset = self.__model__.query
        args = {k: v for (k, v) in request.args.items() if k not in ('page', 'export')}
        if args:
            filters = []
            order = []
            limit = None
            for key, value in args.items():
                if value.startswith('%'):
                    filters.append(getattr(self.__model__, key).like(str(value), escape='/'))
                elif key == 'sort':
                    order.append(getattr(self.__model__, value))
                elif key == 'limit':
                    limit = value
                elif hasattr(self.__model__, key):
                    filters.append(getattr(self.__model__, key) == value)
                else:
                    raise BadRequestException('Invalid field [{}]'.format(key))
                queryset = queryset.filter(*filters).order_by(*order).limit(limit)
        if 'page' in request.args:
            resources = queryset.paginate(int(request.args['page'])).items
        else:
            resources = queryset.all()
        return [r.to_dict() for r in resources]

    def _export(self, collection):
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
        response = jsonify(resource)
        response.status_code = 201
        return response
