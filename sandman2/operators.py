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

    def __call__(self, column, values):
        self.validate(column, values)
        converted = [self.convert(column, value) for value in values]
        return self.filter(column, converted)

    def convert(self, column, value):
        converter = converters.get(utils.column_type(column), default_converter)
        try:
            return converter(column, value)
        except Exception:
            raise exception.BadRequestException('Invalid value "{0}" on field "{1}"'.format(value, column.key))

    def validate(self, column, values):
        pass

    def filter(self, column, values):
        pass

class Equal(Operator):

    def filter(self, column, values):
        if current_app.config.get('CASE_INSENSITIVE') and issubclass(utils.column_type(column), six.string_types):
            return sa.func.upper(column).in_([value.upper() for value in values])
        return column.in_(values)

class NotEqual(Operator):

    def filter(self, column, values):
        if current_app.config.get('CASE_INSENSITIVE') and issubclass(utils.column_type(column), six.string_types):
            return ~sa.func.upper(column).in_([value.upper() for value in values])
        return ~column.in_(values)

class Like(Operator):

    def validate(self, column, values):
        if not issubclass(utils.column_type(column), six.string_types):
            raise exception.BadRequestException('Invalid operator "like" on field "{0}"'.format(column.key))

    def filter(self, column, values):
        attr = 'ilike' if current_app.config.get('CASE_INSENSITIVE') else 'like'
        method = getattr(column, attr)
        return sa.and_(*[method(value) for value in values])

class GreaterThan(Operator):

    def filter(self, column, values):
        return column > max(values)

class GreaterEqual(Operator):

    def filter(self, column, values):
        return column >= max(values)

class LessThan(Operator):

    def filter(self, column, values):
        return column < min(values)

class LessEqual(Operator):

    def filter(self, column, values):
        return column < min(values)

operators = {
    'eq': Equal(),
    'ne': NotEqual(),
    'gt': GreaterThan(),
    'gte': GreaterEqual(),
    'lt': LessThan(),
    'lte': LessEqual(),
    'like': Like(),
}

def parse_operator(key, delimiter):
    parts = key.split(delimiter)
    if len(parts) == 1:
        return parts[0], 'eq'
    elif len(parts) == 2:
        return parts
    raise exception.BadRequestException('Invalid parameter "{0}"'.format(key))

def filter(model, key, values):
    delimiter = current_app.config.get('QUERY_DELIMITER', '__')
    column_name, operator_name = parse_operator(key, delimiter)
    column = utils.get_column(model, column_name)
    try:
        operator = operators[operator_name]
    except KeyError:
        raise exception.BadRequestException('Invalid operator "{0}"'.format(operator_name))
    return operator(column, values)
