"""Tests for sandman2."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from tests.resources import *
from pytest_flask.fixtures import client
exclude_tables = ['Playlist']

def test_get_root(client):
    """Can we GET a list of resources from `/`"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers['Content-type'] == 'application/json'


def test_get_resource(client):
    """Can we GET a resource properly?"""
    response = client.get('/track/1')
    assert response.status_code == 200
    assert '</track/1>; rel=self' in response.headers['Link']
    assert json.loads(response.get_data(as_text=True)) == TRACK_ONE
    assert response.headers['Content-type'] == 'application/json'
    assert response.headers['ETag'] in RESOURCE_ETAGS


def test_get_collection(client):
    """Can we GET a collection of resources properly?"""
    response = client.get('/artist/')
    assert response.status_code == 200
    json_response = json.loads(
        response.get_data(as_text=True))['resources']
    assert len(json_response) == 276
    assert response.headers['Content-type'] == 'application/json'
    assert response.headers['ETag'] in COLLECTION_ETAGS


def test_export_collection(client):
    """Can we export a collection of resources properly?"""
    response = client.get('/genre/?export=True')
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert len(data) == 354
    assert response.headers['Content-type'] == 'text/csv; charset=utf-8'


def test_post(client):
    """Can we POST a new resource properly?"""
    response = client.post(
        '/album/',
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
        '/album/',
        data=json.dumps({
            'ArtistId': 1,
            }),
        headers={'Content-type': 'application/json'})
    assert response.status_code == 400


def test_post_existing(client):
    """Can we POST a new resource properly?"""
    client.post(
        '/artist/',
        data=json.dumps({
            'Name': 'Jeff Knupp',
            }),
        headers={'Content-type': 'application/json'})
    response = client.post(
        '/artist/',
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
    response = client.get('/artist/277')
    assert response.status_code == 404
    response = client.put(
        '/artist/277',
        data=json.dumps(NEW_ARTIST),
        headers={'Content-type': 'application/json'}
        )

    assert response.status_code == 201
    assert json.loads(response.get_data(as_text=True)) == NEW_ARTIST

def test_search_collection(client):
    """Can we GET a collection of resources properly?"""
    response = client.get('/artist/?Name=Calexico')
    assert response.status_code == 200
    json_response = json.loads(
        response.get_data(as_text=True))['resources']
    assert len(json_response) == 1
    assert response.headers['Content-type'] == 'application/json'


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

def test_patch_no_data(client):
    """Do we get an error if we try to PATCH a non-existent resource?"""
    response = client.patch(
        '/artist/1',
        )
    assert response.status_code == 400


def test_post_no_data(client):
    """Do we properly reject a POST with no JSON data?"""
    response = client.post('/artist/')
    json_response = json.loads(response.get_data(as_text=True))
    assert json_response == {'message': 'No data received from request'}


def test_post_unknown_field(client):
    """Do we properly reject a POST with an unknown field?"""
    response = client.post(
        '/artist/',
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
                '"8a4a9037a1eb0a50ed7f8d523e05cfcb",'
                '"8527642c9c0fbbd6807e49c30d93a2c6"'
            },
        )
    assert response.status_code == 304


def test_meta_endpoint(client):
    """Can we retrieve a description of the resource from its 'meta'
    endpoint?"""
    response = client.get('/artist/meta')
    assert json.loads(response.get_data(as_text=True)) == ARTIST_META
