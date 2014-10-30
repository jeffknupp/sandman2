import datetime

from sandman2 import db

class User(db.Model):

    """A user of the blogging application."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)


class Blog(db.Model):

    """An online weblog."""

    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    subheader = db.Column(db.String, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(User)


class Post(db.Model):

    """An individual blog post."""

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    posted_at = db.Column(db.DateTime, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship(User)

    @staticmethod
    def is_valid_get(_, resource):
        """Return False if not given a resource (i.e. the request if for a
        collection)."""
        return resource is not None
