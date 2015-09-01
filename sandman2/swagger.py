import re

from werkzeug.routing import parse_rule

from smore import swagger
from smore.apispec import APISpec
from marshmallow_pagination import schemas
from marshmallow_sqlalchemy import ModelSchema

from sandman2.model import db

def make_spec(app):
    spec = APISpec(
        version='1.0',
        title='sandman2',
        produces=['application/json'],
        plugins=['smore.ext.marshmallow'],
    )
    spec.definition('OffsetInfo', schema=schemas.OffsetInfoSchema)
    for service in getattr(app, '__services__', set()):
        register_service(app, spec, service)
    return spec

def register_service(app, spec, service):
    schema = make_schema(service.__model__, db.session)
    page_schema = make_page_schema(schema)
    register_schemas(spec, schema, page_schema)
    register_rules(app, spec, service, schema, page_schema)

def register_schemas(spec, *schemas):
    for schema in schemas:
        definition = re.sub(r'Schema$', '', schema.__name__)
        schema.__definition__ = definition
        spec.definition(definition, schema=schema)

def register_rules(app, spec, service, schema, page_schema):
    for rule in app.url_map._rules_by_endpoint[service.__name__.lower()]:
        rule_schema = page_schema if rule.defaults else schema
        register_rule(spec, service, rule_schema, rule)

def register_rule(spec, service, schema, rule):
    operations = {}
    path = extract_path(rule.rule)
    for method in rule.methods:
        method = method.lower()
        view = getattr(service, method, None)
        if view is None:
            continue
        operations[method] = {
            'responses': make_resource_response(spec, schema, method),
            'parameters': make_resource_param(service, schema, rule, method),
        }
    spec.add_path(path=path, operations=operations, view=view)

def make_resource_response(spec, schema, method):
    if method == 'delete':
        return {204: {'description': ''}}
    return {200: {'schema': schema, 'description': ''}}

RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')
def extract_path(path):
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
    name = '{0}Schema'.format(model.__name__.capitalize())
    Meta = make_meta(model=model, sqla_session=session)
    return type(name, (ModelSchema, ), {'Meta': Meta})

def make_page_schema(schema):
    model_name = schema.Meta.model.__name__.capitalize()
    name = '{0}PageSchema'.format(model_name)
    Meta = make_meta(
        results_schema_class=schema,
    )
    return type(name, (schemas.OffsetPageSchema, ), {'Meta': Meta})

def make_meta(**attrs):
    return type('Meta', (object, ), attrs)
