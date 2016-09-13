Quickstart
==========

Install
-------

The easiest way to install sandman2 is using ``pip``::

    $ pip install sandman2

``sandman2ctl``
---------------

Once installed, sandman2 provides a command-line utility, ``sandman2ctl``, that
takes your database's URL as a command-line argument and starts a RESTful API
server immediately. Database URLs are `RFC-1738-style <http://rfc.net/rfc1738.html>`_ URLs.
For more information, please read the `SQLAlchemy documentation <http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_ on the matter.

**Note:** When using **SQLite**, use ``pysqlite`` as the driver name (i.e.  ``sqlite+pysqlite:///relative/path/to/db``). 

By default, all database tables will be introspected and made available
as API resources (don't worry if this is not the behavior desired; there are easy ways to
configure the exact behavior of ``sandman2``, discussed later in the documentation).
The default URL for each table is a slash followed by the table's name in all 
lower case (e.g. an "Artist" table would be found at ``localhost:5000/artist/``).

Using Your New REST API
-----------------------

If you've successfully pointed ``sandman2ctl`` at your database, you should see
output like the following::

    $ sandman2ctl 'sqlite+pysqlite:///path/to/sqlite/database'
     * Running on http://0.0.0.0:5000/

The API service is available on port 5000 by default (though this is
configurable). You can interact with your service using ``curl`` or any other HTTP
client.
