"""Tests for sandman2."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath('.'))

import pytest

from sandman2 import get_app, db
from tests.resources import *


TEST_DATABASE_PATH = os.path.join('tests', 'data', 'test_db.sqlite3')
PRISTINE_DATABASE_PATH = os.path.join('tests', 'data', 'db.sqlite3')

shutil.copy(PRISTINE_DATABASE_PATH, TEST_DATABASE_PATH)
APPLICATION = get_app('sqlite+pysqlite:///tests/data/test_db.sqlite3')


@pytest.yield_fixture(scope='function')
def app():
    """Yield the application instance."""
    if os.path.exists(TEST_DATABASE_PATH):
        os.unlink(TEST_DATABASE_PATH)
    shutil.copy(PRISTINE_DATABASE_PATH, TEST_DATABASE_PATH)

    APPLICATION.testing = True

    yield APPLICATION

    with APPLICATION.app_context():
        db.session.remove()
        db.drop_all()
    os.unlink(TEST_DATABASE_PATH)


def test_get_resource(app):
    """Can we GET a resource properly?"""
    with app.test_client() as client:
        response = client.get('/track/1')
        assert response.status_code == 200
        assert '</track/1>; rel=self' in response.headers['Link']
        assert json.loads(response.get_data(as_text=True)) == TRACK_ONE
        assert response.headers['Content-type'] == 'application/json'
        assert response.headers['ETag'] in RESOURCE_ETAGS


def test_get_collection(app):
    """Can we GET a collection of resources properly?"""
    with app.test_client() as client:
        response = client.get('/artist')
        assert response.status_code == 200
        json_response = json.loads(
            response.get_data(as_text=True))['resources']
        assert len(json_response) == 275
        assert response.headers['Content-type'] == 'application/json'
        assert response.headers['ETag'] in COLLECTION_ETAGS


def test_post(app):
    """Can we POST a new resource properly?"""
    with app.test_client() as client:
        response = client.post(
            '/album',
            data=json.dumps({
                'Title': 'Some Title',
                'ArtistId': 1,
                }),
            headers={'Content-type': 'application/json'})
        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == NEW_ALBUM


def test_post_missing_field(app):
    """Do we reject a POST with a missing required field?"""
    with app.test_client() as client:
        response = client.post(
            '/album',
            data=json.dumps({
                'ArtistId': 1,
                }),
            headers={'Content-type': 'application/json'})
        assert response.status_code == 400


def test_post_existing(app):
    """Can we POST a new resource properly?"""
    with app.test_client() as client:
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


def test_put_existing(app):
    """Can we PUT a resource at a specific ID?"""
    with app.test_client() as client:
        response = client.put(
            '/artist/1',
            data=json.dumps(REPLACED_ARTIST),
            headers={'Content-type': 'application/json'}
            )

    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == REPLACED_ARTIST


def test_put_new(app):
    """Can we PUT a resource at *new* ID?"""
    with app.test_client() as client:
        response = client.get('/artist/276')
        assert response.status_code == 404
        response = client.put(
            '/artist/276',
            data=json.dumps(NEW_ARTIST),
            headers={'Content-type': 'application/json'}
            )

    assert response.status_code == 201
    assert json.loads(response.get_data(as_text=True)) == NEW_ARTIST


def test_delete(app):
    """Can we DELETE a resource?"""
    with app.test_client() as client:
        response = client.delete('/album/1')
        assert response.status_code == 204
        response = client.get('/album/1')
        assert response.status_code == 404


def test_patch(app):
    """Can we PATCH an existing resource?"""
    with app.test_client() as client:
        response = client.patch(
            '/artist/1',
            data=json.dumps({'Name': 'Jeff Knupp'}),
            headers={'Content-type': 'application/json'},
            )
        assert response.status_code == 200


def test_post_no_data(app):
    """Do we properly reject a POST with no JSON data?"""
    with app.test_client() as client:
        response = client.post('/artist')
        json_response = json.loads(response.get_data(as_text=True))
        assert json_response == {'message': 'No data received from request'}


def test_post_unknown_field(app):
    """Do we properly reject a POST with an unknown field?"""
    with app.test_client() as client:
        response = client.post(
            '/artist',
            data=json.dumps({'foo': 'bar', 'Name': 'Jeff Knupp'}),
            headers={'Content-type': 'application/json'}
        )
        assert response.status_code == 400
        json_response = json.loads(response.get_data(as_text=True))
        assert json_response == {'message': 'Unknown field [foo]'}


def test_etag_mismatch(app):
    """Do we get a 412 if we don't provide a matching ETag in
    an If-Match header?"""
    with app.test_client() as client:
        response = client.get(
            '/track/1',
            headers={'If-Match': '000,111'}
            )
        assert response.status_code == 412


def test_etag_not_modified(app):
    """Do we get a 304 if we provide a valid If-None-Match header value?"""
    with app.test_client() as client:
        response = client.get(
            '/track/1',
            headers={
                'If-None-Match':
                    '"7bcefa90a6faacf8460b00f0bb217388",'
                    '"8a4a9037a1eb0a50ed7f8d523e05cfcb"'
                },
            )
        assert response.status_code == 304
