"""Test using user-defined models with sandman2."""
import json

from pytest_flask.fixtures import client

from tests.resources import (
    GET_ERROR_MESSAGE,
    INVALID_ACTION_MESSAGE,
    )

model_module = 'tests.user_models'
database = 'blog.sqlite3'

def test_validate_get(client):
    """Do we get back an error message when making a GET request that fails
    validation?"""
    response = client.get('/user/')
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_get_single_resource(client):
    """Do we get back an error message when making a GET request for a
    single resource which fails validation ?"""
    response = client.get('/user/1')
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_get_datetime(client):
    """Do we get back a properly formatted datetime on a model that defines one?"""
    response = client.get('/post/1.0')
    assert response.status_code == 200
    assert response.json['posted_at'] is not None


def test_validate_post(client):
    """Do we get back an error message when making a POST request that fails
    validation?"""
    response = client.post(
        '/user/',
        data=json.dumps({
            'name': 'Jeff Knupp',
            'email': 'jeff@jeffknupp.com',
            }),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_post_existing_resource(client):
    """Do we get back an error message when making a POST request on a resource that already exists?"""
    response = client.post(
        '/user/',
        data=json.dumps({
            'name': 'Jeff Knupp',
            'email': 'jknupp@gmail.com',
            }),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_put_existing(client):
    """Do we get back an error message when making a PUT request for
    an exisitng resource?"""
    response = client.put(
        '/user/1',
        data=json.dumps({
            'name': 'Jeff Knupp',
            'email': 'jeff@jeffknupp.com',
            }),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_put_new(client):
    """Do we get back an error message when making a PUT request for a
    totally new resource?"""
    response = client.put(
        '/user/2',
        data=json.dumps({
            'name': 'Elissa Knupp',
            'email': 'name@email.com',
            }),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_patch(client):
    """Do we get back an error message when making a PATCH request on an
    existing resource?"""
    response = client.patch(
        '/user/1',
        data=json.dumps({
            'name': 'Jeff Knupp',
            }),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_delete(client):
    """Do we get back an error message when making a DELETE request that fails
    validation?"""
    response = client.delete('/user/1')
    assert response.status_code == 400
    assert response.json['message'] == INVALID_ACTION_MESSAGE
