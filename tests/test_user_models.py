"""Test using user-defined models with sandman2."""

from pytest_flask.fixtures import client

from tests.resources import GET_ERROR_MESSAGE

model_module = 'tests.user_models'
database = 'blog.sqlite3'


def test_validate_get(client):
    response = client.get('/post')
    assert response.status_code == 400
    assert response.json['message'] == GET_ERROR_MESSAGE
