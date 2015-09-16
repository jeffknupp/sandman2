"""Test using user-defined models with sandman2."""
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from flask import url_for
from pytest_flask.fixtures import client


model_module = 'tests.automap_models'
database = 'blog.sqlite3'


def test_get_automap_collection(client):
    """Do we see a model's __unicode__ definition being used in the admin?"""
    response = client.get(url_for('blog.index_view'))
    assert response.status_code == 200
    assert 'Jeff Knupp' in response.get_data(as_text=True)
