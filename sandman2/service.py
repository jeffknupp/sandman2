"""Automatically generated REST API services from SQLAlchemy
ORM models or a database introspection."""

# Third-party imports
from sqlalchemy.orm import lazyload
from flask import request, make_response
import flask
from flask.views import MethodView

# Application imports
from sandman2.exception import NotFoundException
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
    response = flask.jsonify(resource.to_dict())
    response = add_link_headers(response, resource.links())
    return response


class Service(MethodView):

    __model__ = None
    __json_collection_name__ = 'resources'

    def delete(self, resource_id):
        resource = self._resource(resource_id)
        db.session().delete(resource)
        db.session().commit()
        return self._no_content_response()

    @etag
    def get(self, resource_id=None):
        if resource_id is None:
            return flask.jsonify({
                self.__json_collection_name__: self._all_resources()
                })
        else:
            return jsonify(self._resource(resource_id))

    def patch(self, resource_id=None):
        resource = self._resource(resource_id)
        resource.update(request.json)
        db.session().merge(resource)
        db.session().commit()
        return jsonify(resource)

    @validate_fields
    def post(self):
        resource = self.__model__.query.filter_by(**request.json).first()
        if resource:
            return self._no_content_response()

        resource = self.__model__(**request.json)
        db.session().add(resource)
        db.session().commit()
        return self._created_response(resource)

    def put(self, resource_id):
        resource = self.__model__.query.get(resource_id)
        if resource:
            resource.update(request.json)
            db.session().merge(resource)
            db.session().commit()
            return jsonify(resource)

        resource = self.__model__(**request.json)
        db.session().add(resource)
        db.session().commit()
        return self._created_response(resource)

    def _resource(self, resource_id):
        resource = self.__model__.query.get(resource_id)
        if not resource:
            raise NotFoundException()
        return resource

    def _all_resources(self):
        resources = self.__model__.query.all()
        return [r.to_dict() for r in resources]

    @staticmethod
    def _no_content_response():
        """Return an HTTP 204 "No Content" response."""
        response = make_response()
        response.status_code = 204
        return response

    @staticmethod
    def _created_response(resource):
        """Return an HTTP 201 "Created" response."""
        response = jsonify(resource)
        response.status_code = 201
        return response
