"""Test using user-defined models with sandman2."""

from flask import url_for

model_module = 'tests.automap_models'
database = 'blog.sqlite3'


def test_get_automap_collection(client):
    """Do we see a model's __unicode__ definition being used in the admin?"""
    res = client.get(url_for('blog.index_view'))
    assert res.status_code == 200
    assert 'Jeff Knupp' in res
