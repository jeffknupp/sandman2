The Admin Interface
===================

In addition to a RESTful API service, sandman2 provides a HTML-based *admin interface*
that allows you to view and manipulate the data in your tables. To access the
admin interface, simply navigate to ``/admin`` once your service is started.

On the left sidebar, you'll see a list of all the services you specified (i.e.
the database tables you chose to include). Clicking one will show the contents
of that table, paginated. You can edit a record by clicking on the pencil icon
or delete a record using the trashcan icon.

You may notice that *foreign keys* are displayed with their default Python
representation (i.e. ``<flask_sqlalchemy.Artist object @ 0xdeadbeef>``). To show
foreign keys in a more useful way, you can define your own extensions to the
classes reflected in the database and add a ``__unicode__`` member function.

Imagine we have a simple blog application consisting of Blog, Post, and User
models. As expected, each post belongs to a specific user and the model has the
requisite foreign key to the User table. When we view a Post's assoicated user
in the admin site, however, we see the following::

    <flask_sqlalchemy.user object at 0x10d3cea10>

To provide a more useful representation in the admin, we *extend* the reflected
class by creating a ``models.py`` file and adding functionality to our model
classes. Deriving from ``sandman2.AutomapModel`` accomplishes this::

    
    from sandman2 import AutomapModel

    class User(AutomapModel):

        """A user of the blogging application."""

        __tablename__ = 'user'

        def __unicode__(self):
            return self.name


    class Blog(AutomapModel):

        """An online weblog."""

        __tablename__ = 'blog'

        def __unicode__(self):
            return self.name

    class Post(AutomapModel):

        """An individual blog post."""

        __tablename__ = 'post'

        def __unicode__(self):
            return self.title

Notice that you can refer to attributes of the class that you know to be present
(like ``user.name``) without defining the ``name`` column; all other
columns/properties are reflected. You're meerly *extending* the existing model
class.
