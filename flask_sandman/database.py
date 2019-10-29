"""Database

Sets up the SQLAlchemy instance used within Sandman.
:attr:`database` is instantiated for the use of :class:`flask_sandman.model.Model` and :meth:`flask_sandman.api.sandman`.
:attr:`database` gets bound within :meth:`flask_sandman.app.application` as illustrated in the `Flask-SQLAlchemy` documentation covering `context <https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/#introduction-into-contexts>`_."""
from flask_sqlalchemy import SQLAlchemy
# Sandman
# from .model import Model

DATABASE = SQLAlchemy() #: An instance of SQLAlchemy that is used universally within Sandman2
# DATABASE = SQLAlchemy(model_class=Model) #: An instance of SQLAlchemy that is used universally within Sandman2

