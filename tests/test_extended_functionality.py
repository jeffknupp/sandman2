"""Tests for non-core functionality in sandman2."""


def test_pagination(client):
    """Do we return paginated results when a 'page' parameter is provided?"""
    res = client.get('/artist?page=2')
    assert res.status_code == 200
    assert len(res.json['resources']) == 20
    assert res.json['resources'][0]['ArtistId'] == 21
