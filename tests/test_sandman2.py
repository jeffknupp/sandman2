"""Tests for sandman2."""
import os
import sys
import json
import datetime

from dateutil.parser import parse as parse_date

sys.path.insert(0, os.path.abspath('.'))

from tests.resources import *
from pytest_flask.fixtures import client


def test_get_resource(client):
    """Can we GET a resource properly?"""
    response = client.get('/track/1')
    assert response.status_code == 200
    assert '</track/1>; rel=self' in response.headers['Link']
    assert json.loads(response.get_data(as_text=True)) == TRACK_ONE
    assert response.headers['Content-type'] == 'application/json'
    assert response.headers['ETag'] in RESOURCE_ETAGS


class TestGetCollection:

    def test_get(self, client):
        """Can we GET a collection of resources properly?"""
        response = client.get('/artist')
        assert response.status_code == 200
        json_response = json.loads(
            response.get_data(as_text=True))['resources']
        assert len(json_response) == 275
        assert response.headers['Content-type'] == 'application/json'
        assert response.headers['ETag'] in COLLECTION_ETAGS

    def test_get_query_bad_column(self, client):
        response = client.get('/artist', query_string='MissingColumn=5')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400
        assert data['message'] == 'Invalid parameter "MissingColumn"'

    def test_get_query_bad_value(self, client):
        response = client.get('/artist', query_string='ArtistId=five')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400
        assert data['message'] == 'Invalid value "five" on field "ArtistId"'

    def test_get_query_bad_key(self, client):
        response = client.get('/artist', query_string='Name__invalid__operator=5')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400
        assert data['message'] == 'Invalid parameter "Name__invalid__operator"'

    def test_get_query_bad_operator(self, client):
        response = client.get('/artist', query_string='Name__missing_operator=5')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400
        assert data['message'] == 'Invalid operator "missing_operator"'

    def test_get_query_equals_string(self, client):
        response = client.get('/artist?Name=AC/DC')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 1
        assert data['resources'][0]['Name'] == 'AC/DC'

    def test_get_query_equals_string_case_insensitive(self, client):
        client.application.config['CASE_INSENSITIVE'] = True
        response = client.get('/artist?Name=ac/dc')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 1
        assert data['resources'][0]['Name'] == 'AC/DC'

    def test_get_query_equals_string_multiple(self, client):
        response = client.get('/artist?Name=AC/DC&Name=Aerosmith')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 2
        assert {'AC/DC', 'Aerosmith'} == set(each['Name'] for each in data['resources'])

    def test_get_query_not_equals(self, client):
        response = client.get('/artist?Name__ne=AC/DC')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 274
        assert not any(each['Name'] == 'AC/DC' for each in data['resources'])

    def test_get_query_not_equals_custom_delimiter(self, client):
        client.application.config['QUERY_DELIMITER'] = '::'
        response = client.get('/artist?Name::ne=AC/DC')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 274
        assert not any(each['Name'] == 'AC/DC' for each in data['resources'])

    def test_get_query_not_equals_multiple(self, client):
        response = client.get('/artist?Name__ne=AC/DC&Name__ne=Aerosmith')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['resources']) == 273
        assert not any(each['Name'] in ['AC/DC', 'Aerosmith'] for each in data['resources'])

    def test_get_query_greater(self, client):
        response = client.get('/artist?ArtistId__gt=5')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert all([each['ArtistId'] > 5 for each in data['resources']])

    def test_get_query_greater_multiple(self, client):
        response = client.get('/artist?ArtistId__gt=5&ArtistId__gt=7')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert all([each['ArtistId'] > 7 for each in data['resources']])

    def test_get_query_less(self, client):
        response = client.get('/invoice?InvoiceDate__lt=2011-01-01')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        date = datetime.datetime(2011, 1, 1)
        assert all([
            parse_date(each['InvoiceDate'], ignoretz=True) < date
            for each in data['resources']
        ])

    def test_get_query_like_bad_column(self, client):
        response = client.get('/artist?ArtistId__like=AC%')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 400
        assert data['message'] == 'Invalid operator "like" on field "ArtistId"'

    def test_get_query_like(self, client):
        response = client.get('/artist?Name__like=AC%')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert all([each['Name'].lower().startswith('ac') for each in data['resources']])

    def test_get_query_like_multiple(self, client):
        response = client.get('/artist?Name__like=AC%&Name__like=Aero%')
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert all([
            each['Name'].lower().startswith('ac') or
            each['Name'].lower().startswith('aero')
            for each in data['resources']
        ])


def test_post(client):
    """Can we POST a new resource properly?"""
    response = client.post(
        '/album',
        data=json.dumps({
            'Title': 'Some Title',
            'ArtistId': 1,
            }),
        headers={'Content-type': 'application/json'})
    assert response.status_code == 201
    assert json.loads(response.get_data(as_text=True)) == NEW_ALBUM


def test_post_missing_field(client):
    """Do we reject a POST with a missing required field?"""
    response = client.post(
        '/album',
        data=json.dumps({
            'ArtistId': 1,
            }),
        headers={'Content-type': 'application/json'})
    assert response.status_code == 400


def test_post_existing(client):
    """Can we POST a new resource properly?"""
    client.post(
        '/artist',
        data=json.dumps({
            'Name': 'Jeff Knupp',
            }),
        headers={'Content-type': 'application/json'})
    response = client.post(
        '/artist',
        data=json.dumps({
            'Name': 'Jeff Knupp',
            }),
        headers={'Content-type': 'application/json'})

    assert response.status_code == 204


def test_put_existing(client):
    """Can we PUT a resource at a specific ID?"""
    response = client.put(
        '/artist/1',
        data=json.dumps(REPLACED_ARTIST),
        headers={'Content-type': 'application/json'}
        )

    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == REPLACED_ARTIST


def test_put_new(client):
    """Can we PUT a resource at *new* ID?"""
    response = client.get('/artist/276')
    assert response.status_code == 404
    response = client.put(
        '/artist/276',
        data=json.dumps(NEW_ARTIST),
        headers={'Content-type': 'application/json'}
        )

    assert response.status_code == 201
    assert json.loads(response.get_data(as_text=True)) == NEW_ARTIST


def test_delete(client):
    """Can we DELETE a resource?"""
    response = client.delete('/album/1')
    assert response.status_code == 204
    response = client.get('/album/1')
    assert response.status_code == 404


def test_patch(client):
    """Can we PATCH an existing resource?"""
    response = client.patch(
        '/artist/1',
        data=json.dumps({'Name': 'Jeff Knupp'}),
        headers={'Content-type': 'application/json'},
        )
    assert response.status_code == 200


def test_post_no_data(client):
    """Do we properly reject a POST with no JSON data?"""
    response = client.post('/artist')
    json_response = json.loads(response.get_data(as_text=True))
    assert json_response == {'message': 'No data received from request'}


def test_post_unknown_field(client):
    """Do we properly reject a POST with an unknown field?"""
    response = client.post(
        '/artist',
        data=json.dumps({'foo': 'bar', 'Name': 'Jeff Knupp'}),
        headers={'Content-type': 'application/json'}
    )
    assert response.status_code == 400
    json_response = json.loads(response.get_data(as_text=True))
    assert json_response == {'message': 'Unknown field [foo]'}


def test_etag_mismatch(client):
    """Do we get a 412 if we don't provide a matching ETag in
    an If-Match header?"""
    response = client.get(
        '/track/1',
        headers={'If-Match': '000,111'}
        )
    assert response.status_code == 412


def test_etag_not_modified(client):
    """Do we get a 304 if we provide a valid If-None-Match header value?"""
    response = client.get(
        '/track/1',
        headers={
            'If-None-Match':
                '"7bcefa90a6faacf8460b00f0bb217388",'
                '"8a4a9037a1eb0a50ed7f8d523e05cfcb"'
            },
        )
    assert response.status_code == 304


def test_meta_endpoint(client):
    """Can we retrieve a description of the resource from its 'meta'
    endpoint?"""
    response = client.get('/artist/meta')
    assert json.loads(response.get_data(as_text=True)) == ARTIST_META
