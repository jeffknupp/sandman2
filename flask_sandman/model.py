"""Module containing code related to *flask_sandman* ORM models.

The primary out come of this module is to provide a base :class:``Model`` for Sandman and any third party packages that extend it.
The module provides a declarative base model, :class:`DeclarativeBase`, for use in the database object and a

`Deferred Base`_ illustrates how to make a :class:`Model` class that supports reflection.
`Declarative Base`_ covers the provisioning of a :class:`Model` class on the ORM that maps to a table in ones database; SQLalchemy by design is simply a database connector the ORM layer is provisional.

..[Deferred Base]:: https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/table_config.html#using-reflection-with-declarative
..[Declarative Base]:: https://flask.palletsprojects.com/en/1.1.x/patterns/sqlalchemy/#declarative
"""
# Standard library imports
import datetime
from decimal import Decimal
# SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
# SQLAlchemy
from sqlalchemy.sql import sqltypes

# Application imports
from .database import DATABASE as db
from .service import Service, register as register_service

# Meta Class
#
# The code below can readily be extended with the following construct to accommodate a meta class [1].
#
# [1] https://flask-sqlalchemy.palletsprojects.com/en/2.x/customizing/#model-metaclass
#
# from sqlalchemy.model import DefaultMeta, Model
#
# class MetaModel(DefaultMeta) :
#     """"""
# class BaseModel(metaclass = MetaModel):
#     """"""
# DeclarativeModel = declarative_base(cls=BaseModel, metaclass=MetaModel, name='Model')
# Model = automap_base(DeclarativeModel)
# DATABASE = SQLAlchemy(model_class=DeclarativeModel)

#class BaseModel(object): # class BaseModel(Model, DeferredReflection):
class Model(object):
    """The flask_sandman Model class is the base class for all RESTful resources.
    There is a one-to-one mapping between a table in the database and a
    :class:`flask_sandman.model.Model`.

    :class:`Model` is used as the declarative/automap'd `base class <baseclass>` for SQLAlchemy; strictly Flask-SQLALchemy.
    It is used within Sandman2 to represent the tables within ones schema and may readily be extended by users.

    .. class:: `Flask-SQLAlchemy : Base Class<https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/>`_
    """
    # [1] Illustrates how one might extend the declarative base class, it might prove useful should one want to integrate Marshmallow into the base class
    # [2] shows how one might register a blue print directly from the ModelView class
    #
    # [1] https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html#mixin-and-custom-base-classes
    # [2] https://stackoverflow.com/a/39441841
    # TODO : The doc string originally referenced a `..baseclass::` directive, I'm not entirely sure which Sphinx module provides such a directive so have replaced this with a reference to a `:class:` role

    #: The relative URL this resource should live at.
    __url__ = None

    #: The API version of this resource (not yet used).
    __version__ = '1'

    #: The HTTP methods this resource supports (default=all).
    __methods__ = {
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'HEAD',
        'OPTIONS'
        }

    @classmethod
    def required(cls):
        """Return a list of all columns required by the database to create the
        resource.

        :param cls: The Model class to gather attributes from
        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            is_autoincrement = 'int' in str(column.type).lower() and column.autoincrement
            if (not column.nullable and not column.primary_key) or (column.primary_key and not is_autoincrement):
                columns.append(column.name)
        return columns

    @classmethod
    def optional(cls):
        """Return a list of all nullable columns for the resource's table.

        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            if column.nullable:
                columns.append(column.name)
        return columns

    @classmethod
    def primary_key(cls):
        """Return the key of the model's primary key field.

        :rtype: string
        """
        return list(
            cls.__table__.primary_key.columns)[  # pylint: disable=no-member
                0].key

    def links(self):
        """Return a dictionary of links to related resources that should be
        included in the *Link* header of an HTTP response.

        :rtype: dict

        """
        link_dict = {'self': self.resource_uri()}
        for relationship in inspect(  # pylint: disable=maybe-no-member
                self.__class__).relationships:
            if 'collection' not in relationship.key:
                instance = getattr(self, relationship.key)
                if instance:
                    link_dict[str(relationship.key)] = instance.resource_uri()
        return link_dict

    def resource_uri(self):
        """Return the URI to this specific resource.

        :rtype: str

        """
        return self.__url__ + '/' + str(getattr(self, self.primary_key()))

    def to_dict(self):
        """Return the resource as a dictionary.

        :rtype: dict
        """
        result_dict = {}
        for column in self.__table__.columns.keys():  # pylint: disable=no-member
            value = result_dict[column] = getattr(self, column, None)
            if isinstance(value, Decimal):
                result_dict[column] = float(result_dict[column])
            elif isinstance(value, datetime.datetime):
                result_dict[column] = value.isoformat()
            elif isinstance(value, datetime.time):
                result_dict[column] = value.strftime("%H:%M:%S")
        return result_dict

    def from_dict(self, data):
        """Update the current instance based on attribute->value items in
        *attributes*.

        :param dict data: Dictionary of attributes to be updated
        :rtype: :class:`sandman2.model.Model`
        """
        for key in data:
            setattr(self, key, data[key])
        return self

    def retrieve(self): # Rename to pull; get might be better still
        return self.to_dict()

    def update(self, data): # Rename to push; put/post might be better still
        return self.from_dict(data)

    @classmethod
    def description(cls):
        """Return a field->data type dictionary describing this model
        as reported by the database.

        :rtype: dict
        """

        description = {}
        for column in cls.__table__.columns:  # pylint: disable=no-member
            column_description = str(column.type)
            if not column.nullable:
                column_description += ' (required)'
            description[column.name] = column_description
        return description

# Currently
DeclarativeModel = declarative_base(cls=(db.Model, Model), name="AutomapModel")
AutomapModel = automap_base(DeclarativeModel)
# DeclarativeModel = declarative_base(cls=(DATABASE.Model, BaseModel), name="AutomapModel") #, name='Model')
# AutomapModel = automap_base(DeclarativeModel) # Changing the name here seems to make both the class and the package fragile for some reason
# Originally :
# DeclarativeModel = declarative_base(cls=BaseModel, name='Model')
# Model = automap_base(DeclarativeModel) # Originally : AutomapModel

def register(router, model):
    """Register *cls* to be included in the API service

    :param model: Class deriving from :class:`flask_sandman.models.Model`
    """
    model.__url__ = '/{}'.format(model.__name__.lower())
    service = type(
        model.__name__ + 'Service',
        (Service,),
        {
            '__model__': model,
        })

    # inspect primary key
    # composite keys not supported (yet)
    # types defined at http://flask.pocoo.org/docs/0.10/api/#url-route-registrations
    cols = list(model.__table__.primary_key.columns)
    if len(cols) == 1:
        # types defined at http://flask.pocoo.org/docs/0.10/api/#url-route-registrations
        primary_key_type = {
            sqltypes.String : 'string',
            sqltypes.Integer: 'int',
            sqltypes.Numeric: 'float'}.get(cols[0].type, 'string')
        # Originally :
        # col_type = cols[0].type
        # if isinstance(col_type, sqltypes.String):
        #     primary_key_type = 'string'
        # elif isinstance(col_type, sqltypes.Integer):
        #     primary_key_type = 'int'
        # elif isinstance(col_type, sqltypes.Numeric):
        #     primary_key_type = 'float'
    else:
        # composite keys not supported (yet)
        primary_key_type = 'string'


    # registration
    register_service(router, service, primary_key_type)
    return service

__all__ = ["BaseModel", "AutomapModel"]
