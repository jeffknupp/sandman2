import re

from smore import swagger
from smore.apispec import APISpec
from werkzeug.routing import parse_rule
from marshmallow_sqlalchemy import ModelSchema

from sandman2.model import db

def make_spec(app):
    spec = APISpec(
        version='1.0',
        title='sandman2',
        produces=['application/json'],
        plugins=['smore.ext.marshmallow'],
    )
    for service in getattr(app, '__services__', set()):
        register_swagger_service(app, spec, service)
    return spec

def register_swagger_service(app, spec, service):
    schema = make_schema(service.__model__, db.session)
    spec.definition(service.__model__.__name__.capitalize(), schema=schema())
    for rule in app.url_map._rules_by_endpoint[service.__name__.lower()]:
        operations = {}
        path = extract_path(rule.rule)
        for method in rule.methods:
            method = method.lower()
            view = getattr(service, method, None)
            if view is None:
                continue
            operations[method] = {
                'responses': make_resource_response(service, schema, method),
                'parameters': make_resource_param(service, schema, rule, method),
            }
        spec.add_path(path=path, operations=operations, view=view)

def make_resource_response(service, schema, method):
    if method == 'delete':
        return {204: {'description': ''}}
    definition = '#/definitions/{0}'.format(service.__model__.__name__.capitalize())
    return {200: {'$ref': definition}}

RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')
def extract_path(path):
    '''
    Transform a Flask/Werkzeug URL pattern in a Swagger one.
    '''
    return RE_URL.sub(r'{\1}', path)

def make_resource_param(service, schema, rule, method):
    if not any(variable == 'resource_id' for _, _, variable in parse_rule(rule.rule)):
        return []
    param = {
        'in': 'path',
        'name': 'resource_id',
        'description': '',
        'required': True,
    }
    param.update(get_resource_type(service, schema))
    return [param]

def get_resource_type(service, schema):
    key = service.__model__.__mapper__.primary_key[0]
    field = schema._declared_fields[key.key]
    type, format = swagger._get_json_type_for_field(field)
    if format:
        return {'type': type, 'format': format}
    return {'type': type}

def make_schema(model, session):
    name = '{0}Schema'.format(model.__name__.capitalize)
    Meta = type(
        'Meta',
        (object, ),
        {
            'model': model,
            'sqla_session': session,
        },
    )
    return type(
        name,
        (ModelSchema, ),
        {'Meta': Meta},
    )
