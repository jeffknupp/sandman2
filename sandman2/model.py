"""Model class for the sandman2 application."""
from decimal import Decimal

from sqlalchemy.inspection import inspect
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Model(object):

    __url__ = None
    __version__ = '1'
    __methods__ = set(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    
    @classmethod
    def required(cls):
        columns = []
        for column in cls.__table__.columns:
            if not column.nullable and not column.primary_key:
                columns.append(column.name)
        return columns

    @classmethod
    def optional(cls):
        columns = []
        for column in cls.__table__.columns:
            if column.nullable:
                columns.append(column.name)
        return columns

    def related_objects(self):
        object_list = []
        for resource in list(self.__table__.foreign_keys):
            object_list.append(resource.column.table)
        return object_list

    def primary_key(self):
        return list(self.__table__.primary_key.columns)[0].name

    def to_dict(self):
        result_dict = {}
        for column in self.__table__.columns.keys():
            result_dict[column] = getattr(self, column, None)
            if isinstance(result_dict[column], Decimal):
                result_dict[column] = str(result_dict[column])
        return result_dict

    def links(self):
        link_dict = {'self': self.resource_uri()}
        for relationship in inspect(self.__class__).relationships:
            if 'collection' not in relationship.key:
                instance = getattr(self, relationship.key)
                if instance:
                    link_dict[str(relationship.key)] = instance.resource_uri()
        return link_dict

    def resource_uri(self):
        return self.__url__ + '/' + str(getattr(self, self.primary_key()))

    def update(self, attributes):
        """Update the current instance based on attribute->value items in
        *attributes*."""
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self

    def __str__(self):
        return str(self.to_dict())
