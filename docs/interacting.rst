Basics
======

sandman2 exposes each table in your database as a ``resource`` in a RESTful API
service. You access and manipulate resources by sending HTTP requests with
various ``methods`` (e.g. ``GET``, ``POST``, ``DELETE``, etc.). Here's a quick
list of common tasks and the HTTP method to use to complete them:

Retrieve all records in a table
-------------------------------

In REST-terms, a table in your database represents a ``resource``. A *group* of
resources (i.e. data returned from a ``SELECT * FROM foo`` statement)
is called a ``collection``. To retrieve a ``collection`` of resources from your
API, make a HTTP ``GET`` call to the resource's base URL. By default, this is
set to ``/<table_name_in_lowercase>``. If you had an ``Artist`` table in your
database, you would use the following ``curl`` command to retrieve the collection 
of all ``Artist`` resources::

    $ curl http://127.0.0.1:5000/artist

The implied HTTP method in this case is ``GET``. The response would be a JSON list of
all the artist resources in the database.

Possible HTTP status codes for response
```````````````````````````````````````

* ``200 OK`` if the resource is found
* ``404 Not Found`` if the resource can't be found


Retrieve a single row
---------------------

To retrieve a single resource (i.e. row in your database), use the ``GET``
method while specifying the value of the resource's primary key field. If our
``Artist`` table used the column ``ArtistId`` as a primary key, we could
retrieve a single resource like so::

    $ curl http://127.0.0.1:5000/artist/3

Again, the implied HTTP method is ``GET``.

Possible HTTP status codes for response
```````````````````````````````````````

* ``200 OK`` if the resource is found
* ``404 Not Found`` if the resource can't be found

Add a new row to a table
------------------------

To add a resource to an existing collection, use the HTTP ``POST`` method on the
collection's URL (e.g. ``/artist`` in our example). All required fields should
be sent as JSON data, and the ``Content-type`` header should be set to
``application/json``. Here's how we would create a new ``artist`` resource::

    $ curl -X POST -d '{"Name": "Jeff Knupp"}' -H "Content-Type: application/json" http://127.0.0.1:5000/artist

In this case, the primary key field (``ArtistId``) was not sent, since it is an
auto-incremented integer. The response shows the assigned ``ArtistId``::

    {
        "ArtistId": 276,
        "Name": "Jeff Knupp"
    }

Possible HTTP status codes for response
```````````````````````````````````````

* ``201 Created`` if a new resource is properly created
* ``400 Bad Request`` if the request is malformed or missing data

Error conditions
````````````````

If we send a field not in the record's definition, we are alerted by sandman2 in
the HTTP response::

    $ curl -X POST -d '{"Name": "Jeff Knupp2", "Age": 32}' -H "Content-Type: application/json" http://127.0.0.1:5000/artist
    {
        "message": "Unknown field [Age]"
    }

Similarly, if we miss a required field, sandman2 helpfully lets us know which
field(s) we missed. Imagine we had an ``Album`` table that contains albums for
each artist. Each row has the album's title in the ``Title`` column and the
associated ``Artist``'s ``ArtistId`` in the ``ArtistId`` column. If we try to
create a new album with only a ``Title`` set, the following is returned::

    $ curl -X POST -d '{"Title": "For Those About To Rock We Salute You"}' -H "Content-Type: application/json" http://127.0.0.1:5000/album
    {
        "message": "[ArtistId] required"
    }

Delete a single row from a table
--------------------------------

To remove a resource from a collection, use the HTTP ``DELETE`` method while
specifying a value for the primary key field::

    $ curl -X DELETE http://127.0.0.1:5000/artist/276

Possible HTTP status codes for response
```````````````````````````````````````

* ``204 No Content`` if the resource was found and deleted
* ``404 Not Found`` if the resource could not be found

Update an existing row
----------------------

To update a row, send an HTTP ``PATCH`` request to the service containing only
the fields and values you want to change. To change the ``ArtistId`` associated
with an album, you could send the following ``PATCH`` request::

    $ curl -X PATCH -d '{"ArtistId": 3}' -H "Content-Type: application/json" http://127.0.0.1:5000/album/6

This updates the ``Album`` with ID ``6`` to refer to the ``Artist`` with ID ``3``.

Possible HTTP status codes for response
```````````````````````````````````````

* ``200 OK`` if the resource was found and updated
* ``400 Bad Request`` if the request is malformed or missing data
* ``404 Not Found`` if the resource could not be found


"Upsert" a row in a table
-------------------------

Some database engines support an "upsert" action where a full row is provided,
including a value for the primary key. If no record with that primary key
exists, the row is inserted as normal. If there *is* an existing row with the
same primary key value, the operation is changed to an "update", and the
existing row is updated with the new values.

The HTTP ``PUT`` method works in much the same way. A full copy of a
resource is sent in the request. The primary key value is determined by the URL
the request is sent to (i.e. a ``PUT`` to ``/artist/3`` implies an ``ArtistId``
of ``3``). Any existing resource is overwritten with the new values.

An important property of the HTTP ``PUT`` is *idempotency*. An *idempotent*
operation always gives the same result, regardless of how many times or in which
order it is applied. You can always be sure of the state of a resource after a
successful ``PUT`` request.

Possible HTTP status codes for response
```````````````````````````````````````

* ``200 OK`` if the resource was found and updated
* ``201 Created`` if the resource was not found and a new resource was created
* ``400 Bad Request`` if the request is malformed or missing data
