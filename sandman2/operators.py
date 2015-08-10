# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime

import six
import sqlalchemy as sa
from flask import current_app
from dateutil.parser import parse as parse_date

from sandman2 import utils
from sandman2 import exception

converters = {
    datetime.datetime: lambda column, value: parse_date(value),
    datetime.date: lambda column, value: parse_date(value).date,
}
def default_converter(column, value):
    column_type = utils.column_type(column)
    return column_type(value)

class Operator(object):

    def __call__(self, column, value):
        self.validate(column, value)
        return self.filter(column, self.convert(column, value))

    def convert(self, column, value):
        converter = converters.get(utils.column_type(column), default_converter)
        try:
            return converter(column, value)
        except Exception as error:
            raise exception.BadRequestException('Invalid value "{0}" on field "{1}"'.format(value, column.key))

    def validate(self, column, value):
        pass

    def filter(self, column, value):
        pass

class Equal(Operator):

    def filter(self, column, value):
        if current_app.config.get('CASE_INSENSITIVE') and issubclass(utils.column_type(column), six.string_types):
            return sa.func.upper(column) == value.upper()
        return column == value

class Like(Operator):

    def validate(self, column, value):
        if not issubclass(utils.column_type(column), six.string_types):
            raise exception.BadRequestException('Invalid operator "like" on field "{0}"'.format(column.key))

    def filter(self, column, value):
        attr = 'ilike' if current_app.config.get('CASE_INSENSITIVE') else 'like'
        return getattr(column, attr)(value)

class GreaterThan(Operator):

    def filter(self, column, value):
        return column > value

class GreaterEqual(Operator):

    def filter(self, column, value):
        return column >= value

class LessThan(Operator):

    def filter(self, column, value):
        return column < value

class LessEqual(Operator):

    def filter(self, column, value):
        return column < value

operators = {
    'eq': Equal(),
    'gt': GreaterThan(),
    'gte': GreaterEqual(),
    'lt': LessThan(),
    'lte': LessEqual(),
    'like': Like(),
}

def parse_operator(key):
    parts = key.split('__')
    if len(parts) == 1:
        return parts[0], 'eq'
    elif len(parts) == 2:
        return parts
    raise exception.BadRequestException('Invalid parameter "{0}"'.format(key))

def filter(model, key, value):
    column_name, operator_name = parse_operator(key)
    column = utils.get_column(model, column_name)
    try:
        operator = operators[operator_name]
    except KeyError:
        raise exception.BadRequestException('Invalid operator "{0}"'.format(operator_name))
    return operator(column, value)
