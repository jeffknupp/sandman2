"""Tests for non-core functionality in sandman2."""

from pytest_flask.fixtures import client

def test_pagination(client):
    """Do we return paginated results when a 'page' parameter is provided?"""
    response = client.get('/artist?page=2')
    assert response.status_code == 200
    assert len(response.json['resources']) == 20
    assert response.json['resources'][0]['ArtistId'] == 21
