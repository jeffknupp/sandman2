from flask_sandman.database import DATABASE as db
from flask_sandman.exception import register as register_exceptions
from flask_sandman.model import Model, AutomapModel, register as register_model


def sandman(application, user_models, exclude_tables, admin, read_only, schema, reflect_all) :
    # Sandman Exceptions
    register_exceptions(application)
    # Router
    router = application
    with application.app_context():
        if user_models:
            if any([issubclass(cls, AutomapModel) for cls in user_models]):
                AutomapModel.prepare(  # pylint:disable=maybe-no-member
                    db.engine, reflect=True, schema=schema)

            for user_model in user_models:
                register_model(user_model, admin)
        elif reflect_all:
            AutomapModel.prepare(  # pylint:disable=maybe-no-member
                db.engine, reflect=True, schema=schema)
            for cls in AutomapModel.classes:
                if exclude_tables and cls.__table__.name in exclude_tables:
                    continue
                if read_only:
                    cls.__methods__ = {'GET'}
                register_model(cls, admin)    # with application.app_context():

