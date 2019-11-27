"""Sandman2 main application setup code."""
# Flask
from flask import Flask, current_app, jsonify
# Flask: Admin
from flask_admin import Admin
# Flask: HTTP Auth
# from flask_httpauth import HTTPBasicAuth
# Sandman
from .api import sandman

# Augment flask_sandman's Model class with the Automap and Flask-SQLAlchemy model classes
# auth = HTTPBasicAuth()

def application(
        database_uri,
        exclude_tables=[],
        include_models=[],
        read_only=True,
        schema=None):
    """Return an application instance connected to the database described in
    *database_uri*.

    :param str database_uri: The URI connection string for the database
    :param list exclude_tables: A list of tables to exclude from the API
                                service
    :param list include_models: A list of user-defined models to include in the
                             API service
    :param bool read_only: Only allow HTTP GET commands for all endpoints
    :param str schema: Use the specified named schema instead of the default
    """
    app = Flask('flask_sandman')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SANDMAN2_READ_ONLY'] = read_only
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.classes = []
    # Database
    from .database import DATABASE as db
    db.init_app(app)
    app.database = db
    # Administration
    from .admin import administration
    # admin = Admin(app, base_template = 'layout.html', template_mode = 'bootstrap3')
    admin = administration(app)
    # Sandman
    sandman(app, database=db, include_models=include_models or [], exclude_tables=exclude_tables or [], read_only=read_only, admin = admin, schema=schema)
    return app

