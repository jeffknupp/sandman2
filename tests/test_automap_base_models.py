"""Test using user-defined models with sandman2."""
import json

from pytest_flask.fixtures import client

from tests.resources import (
    GET_ERROR_MESSAGE,
    INVALID_ACTION_MESSAGE,
    )

model_module = 'tests.automap_models'
database = 'blog.sqlite3'


def test_get_automap_collection(client):
    """Do we see a model's __unicode__ definition being used in the admin?"""
    response = client.get('/admin/blogview/')
    assert response.status_code == 200
    assert 'Jeff Knupp' in response.data
