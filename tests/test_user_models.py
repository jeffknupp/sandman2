"""Test using user-defined models with sandman2."""

from tests.resources import INVALID_ACTION_MESSAGE

model_module = 'tests.user_models'
database = 'blog.sqlite3'


def test_validate_get(client):
    """Do we get back an error message when making a GET request that fails
    validation?"""
    res = client.get('/user', expect_errors=True)
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_get_single_resource(client):
    """Do we get back an error message when making a GET request for a
    single resource which fails validation ?"""
    res = client.get('/user/1', expect_errors=True)
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_post(client):
    """Do we get back an error message when making a POST request that fails
    validation?"""
    res = client.post_json(
        '/user',
        {
            'name': 'Jeff Knupp',
            'email': 'jeff@jeffknupp.com',
        },
        expect_errors=True,
    )
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_post_existing_resource(client):
    """Do we get back an error message when making a POST request 
    on a resource that already exists?"""
    res = client.post_json(
        '/user',
        {
            'name': 'Jeff Knupp',
            'email': 'jknupp@gmail.com',
        },
        expect_errors=True,
    )
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_put_existing(client):
    """Do we get back an error message when making a PUT request for
    an exisitng resource?"""
    res = client.put_json(
        '/user/1',
        {
            'name': 'Jeff Knupp',
            'email': 'jeff@jeffknupp.com',
        },
        expect_errors=True,
    )
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_put_new(client):
    """Do we get back an error message when making a PUT request for a
    totally new resource?"""
    res = client.put_json(
        '/user/2',
        {
            'name': 'Elissa Knupp',
            'email': 'name@email.com',
        },
        expect_errors=True,
    )
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_patch(client):
    """Do we get back an error message when making a PATCH request on an
    existing resource?"""
    res = client.patch_json('/user/1', {'name': 'Jeff Knupp'}, expect_errors=True)
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE


def test_validate_delete(client):
    """Do we get back an error message when making a DELETE request that fails
    validation?"""
    res = client.delete('/user/1', expect_errors=True)
    assert res.status_code == 400
    assert res.json['message'] == INVALID_ACTION_MESSAGE
