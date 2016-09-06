import datetime

from sandman2.model import db, Model

from tests.resources import (
    GET_ERROR_MESSAGE,
    INVALID_ACTION_MESSAGE,
    )

class User(db.Model, Model):

    """A user of the blogging application."""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)

    @staticmethod
    def is_valid_get(request, resource):
        """Return error message in all cases (just for testing)."""
        return INVALID_ACTION_MESSAGE

    @staticmethod
    def is_valid_post(request, resource):
        """Return error message in all cases (just for testing)."""
        return INVALID_ACTION_MESSAGE

    @staticmethod
    def is_valid_patch(request, resource):
        """Return error message in all cases (just for testing)."""
        return INVALID_ACTION_MESSAGE

    @staticmethod
    def is_valid_put(request, resource):
        """Return error message in all cases (just for testing)."""
        return INVALID_ACTION_MESSAGE

    @staticmethod
    def is_valid_delete(request, resource):
        """Return error message in all cases (just for testing)."""
        return INVALID_ACTION_MESSAGE


class Blog(db.Model, Model):

    """An online weblog."""

    __tablename__ = 'blog'

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    subheader = db.Column(db.String, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(User)


class Post(db.Model, Model):

    """An individual blog post."""

    __tablename__ = 'post'

    id = db.Column(db.Numeric, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    posted_at = db.Column(db.DateTime, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship(User)
