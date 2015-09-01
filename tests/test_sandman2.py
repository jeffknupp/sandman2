"""Tests for sandman2."""
import os
import sys
import datetime

from dateutil.parser import parse as parse_date

sys.path.insert(0, os.path.abspath('.'))

from tests.resources import *  # noqa


def test_get_resource(client):
    """Can we GET a resource properly?"""
    res = client.get('/track/1')
    assert '</track/1>; rel=self' in res.headers['Link']
    assert res.json == TRACK_ONE
    assert res.headers['Content-type'] == 'application/json'
    assert res.headers['ETag'] in RESOURCE_ETAGS


class TestGetCollection:

    def test_get(self, client):
        """Can we GET a collection of resources properly?"""
        res = client.get('/artist')
        assert res.json['pagination']['count'] == 275
        assert res.headers['Content-type'] == 'application/json'
        assert res.headers['ETag'] in COLLECTION_ETAGS

    def test_get_query_bad_column(self, client):
        res = client.get('/artist', {'MissingColumn': '5'}, expect_errors=True)
        assert res.status_code == 400
        assert res.json['message'] == 'Invalid parameter "MissingColumn"'

    def test_get_query_bad_value(self, client):
        res = client.get('/artist', {'ArtistId': 'five'}, expect_errors=True)
        assert res.status_code == 400
        assert res.json['message'] == 'Invalid value "five" on field "ArtistId"'

    def test_get_query_bad_key(self, client):
        res = client.get('/artist', {'Name__invalid__operator': '5'}, expect_errors=True)
        assert res.status_code == 400
        assert res.json['message'] == 'Invalid parameter "Name__invalid__operator"'

    def test_get_query_bad_operator(self, client):
        res = client.get('/artist', {'Name__missing_operator': '5'}, expect_errors=True)
        assert res.status_code == 400
        assert res.json['message'] == 'Invalid operator "missing_operator"'

    def test_get_query_equals_string(self, client):
        res = client.get('/artist', {'Name': 'AC/DC'})
        assert len(res.json['resources']) == 1
        assert res.json['resources'][0]['Name'] == 'AC/DC'

    def test_get_query_equals_string_case_insensitive(self, client):
        client.app.config['CASE_INSENSITIVE'] = True
        res = client.get('/artist', {'Name': 'ac/dc'})
        assert len(res.json['resources']) == 1
        assert res.json['resources'][0]['Name'] == 'AC/DC'

    def test_get_query_equals_string_multiple(self, client):
        res = client.get('/artist?Name=AC/DC&Name=Aerosmith')
        assert len(res.json['resources']) == 2
        assert {'AC/DC', 'Aerosmith'} == set(each['Name'] for each in res.json['resources'])

    def test_get_query_not_equals(self, client):
        res = client.get('/artist?Name__ne=AC/DC')
        assert res.json['pagination']['count'] == 274
        assert not any(each['Name'] == 'AC/DC' for each in res.json['resources'])

    def test_get_query_not_equals_custom_delimiter(self, client):
        client.app.config['QUERY_DELIMITER'] = '::'
        res = client.get('/artist', {'Name::ne': 'AC/DC'})
        assert res.json['pagination']['count'] == 274
        assert not any(each['Name'] == 'AC/DC' for each in res.json['resources'])

    def test_get_query_not_equals_multiple(self, client):
        res = client.get('/artist', {'Name__ne': ['AC/DC', 'Aerosmith']})
        assert res.json['pagination']['count'] == 273
        assert not any(each['Name'] in ['AC/DC', 'Aerosmith'] for each in res.json['resources'])

    def test_get_query_greater(self, client):
        res = client.get('/artist', {'ArtistId__gt': '5'})
        assert all([each['ArtistId'] > 5 for each in res.json['resources']])

    def test_get_query_greater_multiple(self, client):
        res = client.get('/artist', {'ArtistId__gt': ['5', '7']})
        assert all([each['ArtistId'] > 7 for each in res.json['resources']])

    def test_get_query_less(self, client):
        res = client.get('/invoice', {'InvoiceDate__lt': '2011-01-01'})
        date = datetime.datetime(2011, 1, 1)
        assert all([
            parse_date(each['InvoiceDate'], ignoretz=True) < date
            for each in res.json['resources']
        ])

    def test_get_query_like_bad_column(self, client):
        res = client.get('/artist', {'ArtistId__like': 'AC%'}, expect_errors=True)
        assert res.status_code == 400
        assert res.json['message'] == 'Invalid operator "like" on field "ArtistId"'

    def test_get_query_like(self, client):
        res = client.get('/artist', {'Name__like': 'AC%'})
        assert all([each['Name'].lower().startswith('ac') for each in res.json['resources']])

    def test_get_query_like_multiple(self, client):
        res = client.get('/artist', {'Name__like': ['AC%', 'Aero%']})
        assert all([
            each['Name'].lower().startswith('ac') or
            each['Name'].lower().startswith('aero')
            for each in res.json['resources']
        ])

    def test_get_query_sort(self, client):
        res = client.get('/track', {'sort': 'Name'})
        resources = res.json['resources']
        assert resources == sorted(resources, key=lambda r: r['Name'])

    def test_get_query_sort_multiple(self, client):
        res = client.get('/track', {'sort': ['Name', 'Milliseconds']})
        resources = res.json['resources']
        assert resources == sorted(resources, key=lambda r: (r['Name'], r['Milliseconds']))

    def test_get_query_sort_descending(self, client):
        res = client.get('/track', {'sort': '-Name'})
        resources = res.json['resources']
        assert resources == sorted(resources, key=lambda r: r['Name'], reverse=True)


def test_post(client):
    """Can we POST a new resource properly?"""
    res = client.post_json(
        '/album',
        {
            'Title': 'Some Title',
            'ArtistId': 1,
        },
    )
    assert res.status_code == 201
    assert res.json == NEW_ALBUM


def test_post_missing_field(client):
    """Do we reject a POST with a missing required field?"""
    res = client.post_json('/album', {'ArtistId': 1}, expect_errors=True)
    assert res.status_code == 400


def test_post_existing(client):
    """Can we POST a new resource properly?"""
    client.post_json('/artist', {'Name': 'Jeff Knupp'})
    res = client.post_json('/artist', {'Name': 'Jeff Knupp'})
    assert res.status_code == 204


def test_put_existing(client):
    """Can we PUT a resource at a specific ID?"""
    res = client.put_json('/artist/1', REPLACED_ARTIST)
    assert res.json == REPLACED_ARTIST


def test_put_new(client):
    """Can we PUT a resource at *new* ID?"""
    res = client.get('/artist/276', expect_errors=True)
    assert res.status_code == 404
    res = client.put_json('/artist/276', NEW_ARTIST)
    assert res.status_code == 201
    assert res.json == NEW_ARTIST


def test_delete(client):
    """Can we DELETE a resource?"""
    res = client.delete('/album/1')
    assert res.status_code == 204
    res = client.get('/album/1', expect_errors=True)
    assert res.status_code == 404


def test_patch(client):
    """Can we PATCH an existing resource?"""
    client.patch_json('/artist/1', {'Name': 'Jeff Knupp'})


def test_post_no_data(client):
    """Do we properly reject a POST with no JSON data?"""
    res = client.post('/artist', expect_errors=True)
    assert res.json == {'message': 'No data received from request'}


def test_post_unknown_field(client):
    """Do we properly reject a POST with an unknown field?"""
    res = client.post_json('/artist', {'foo': 'bar', 'Name': 'Jeff Knupp'}, expect_errors=True)
    assert res.status_code == 400
    assert res.json == {'message': 'Unknown field [foo]'}


def test_etag_mismatch(client):
    """Do we get a 412 if we don't provide a matching ETag in
    an If-Match header?"""
    res = client.get('/track/1', headers={'If-Match': '000,111'}, expect_errors=True)
    assert res.status_code == 412


def test_etag_not_modified(client):
    """Do we get a 304 if we provide a valid If-None-Match header value?"""
    res = client.get(
        '/track/1',
        headers={
            'If-None-Match':
                '"7bcefa90a6faacf8460b00f0bb217388",'
                '"8a4a9037a1eb0a50ed7f8d523e05cfcb"'
        },
    )
    assert res.status_code == 304


def test_meta_endpoint(client):
    """Can we retrieve a description of the resource from its 'meta'
    endpoint?"""
    res = client.get('/artist/meta')
    assert res.json == ARTIST_META
