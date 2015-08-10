# -*- coding: utf-8 -*-

from sandman2 import exception

def get_column(model, key):
    try:
        return getattr(model, key)
    except AttributeError:
        raise exception.BadRequestException('Invalid parameter "{0}"'.format(key))

def column_type(attribute):
    columns = attribute.property.columns
    if len(columns) == 1:
        return columns[0].type.python_type
    return None
