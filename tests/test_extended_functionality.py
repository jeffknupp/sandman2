"""Tests for non-core functionality in flask_sandman."""

from pytest_flask.fixtures import client

read_only = True

def test_pagination(client):
    """Do we return paginated results when a 'page' parameter is provided?"""
    response = client.get('/artist/?page=2')
    assert response.status_code == 200
    assert len(response.json) == 20
    assert response.json[0]['ArtistId'] == 21


def test_filtering(client):
    """Do we return filtered results when a URL parameter is provided?"""
    response = client.get('/artist/?Name=AC/DC')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['ArtistId'] == 1


def test_filtering_unkown_field(client):
    """Do we return filtered results when a URL parameter is provided?"""
    response = client.get('/artist/?Foo=AC/DC')
    assert response.status_code == 400


def test_wildcard_filtering(client):
    """Do we return filtered results when a wildcarded URL parameter is provided?"""
    response = client.get('/artist/?Name=%25%25DC')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['ArtistId'] == 1


def test_sorting(client):
    """Do we return sorted results when a 'sort' URL parameter is provided?"""
    response = client.get('/artist/?sort=Name')
    assert response.status_code == 200
    assert len(response.json) == 276
    assert response.json[0]['ArtistId'] == 43


def test_sorting_descending(client):
    """Can we sort results in descending order?"""
    response = client.get('/artist/?sort=-Name')
    assert response.status_code == 200
    assert len(response.json) == 276
    assert response.json[0]['ArtistId'] == 155


def test_limit(client):
    """Do we return sorted results when a 'limit' URL parameter is provided?"""
    response = client.get('/artist/?limit=5')
    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[0]['ArtistId'] == 1


def test_sort_limit_and_pagination(client):
    """Can we combine filtering parameters to get targeted results?"""
    response = client.get('/artist/?limit=2&sort=ArtistId&page=2')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['ArtistId'] == 3
