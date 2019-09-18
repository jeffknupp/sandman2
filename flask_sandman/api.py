from flask_sandman.database import DATABASE as db
from flask_sandman.exception import register as register_exceptions
from flask_sandman.model import Model, AutomapModel, register as register_model


def sandman(app,user_models, exclude_tables, admin, read_only, schema, reflect_all) :
    register_exceptions(app)
    if user_models:
        with app.app_context():
            _register_user_models(user_models, admin, schema=schema)
    elif reflect_all:
        with app.app_context():
            _reflect_all(exclude_tables, admin, read_only, schema=schema)

def _register_user_models(user_models, admin=None, schema=None):
    """Register any user-defined models with the API Service.

    :param list user_models: A list of user-defined models to include in the
                             API service
    """
    if any([issubclass(cls, AutomapModel) for cls in user_models]):
        AutomapModel.prepare(  # pylint:disable=maybe-no-member
                               db.engine, reflect=True, schema=schema)

    for user_model in user_models:
        register_model(user_model, admin)


def _reflect_all(exclude_tables=None, admin=None, read_only=False, schema=None):
    """Register all tables in the given database as services.

    :param list exclude_tables: A list of tables to exclude from the API
                                service
    """
    AutomapModel.prepare(  # pylint:disable=maybe-no-member
        db.engine, reflect=True, schema=schema)
    for cls in AutomapModel.classes:
        if exclude_tables and cls.__table__.name in exclude_tables:
            continue
        if read_only:
            cls.__methods__ = {'GET'}
        register_model(cls, admin)