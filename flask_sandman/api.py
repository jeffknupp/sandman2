from .database import DATABASE as db
from .exception import register as register_exceptions
from .model import AutomapModel, Model as BaseModel, register as register_model_view
from .views import register as register_index
from .admin import AdminView, register as register_admin_view

def sandman(application, database = db, blueprint = None, include_models = [], exclude_tables = [], read_only = True, admin = None, root = "/", admin_view = AdminView, schema = None):
    """"""
    # Sandman Exceptions
    register_exceptions(application)
    # Router
    router = blueprint or application
    # app = app or current_app
    # api = api or app
    with application.app_context():
        # Database Tables
        router.included_models, router.excluded_models = register_entities(database, include_models = include_models, exclude_tables = exclude_tables, read_only = read_only, schema = schema)
        # router.models = router.included_models + router.excluded_models # Mostly used for development
        router.model_views = []
        router.admin_views = []
        for model in router.included_models:
            # Model Views
            router.model_views.append(register_model_view(router, model))
            # Admin Views
            if admin:
                router.admin_views.append(register_admin_view(admin, model, view = admin_view))
        # API Index
        if root: register_index(router, root)
    return router


def register_entities(database, include_models = [], exclude_tables = [], read_only = True, schema = None, automodel = AutomapModel):
    models = []
    tablename = lambda model : getattr(getattr(model, "__table__"), "name", "") if hasattr(model, "__table__") else getattr(model, "__tablename__", "")
    automodel.prepare(database.engine, reflect=True, schema=schema)
    # if include_models :
    for model in include_models:
        models.append(model)
    tables = [tablename(model) for model in models]
    # else :
    for model in automodel.classes:
        if tablename(model) in tables: # Prevents including an automatically mapped model that has been overwritten by a custom model listed in included_models
            continue
        if read_only:
            model.__methods__ = {'GET'} # TODO : Can this safely include HEAD and OPTIONS requests ?
        models.append(model)
    # return models
    include, exclude = [], []
    [exclude.append(model) if tablename(model) in exclude_tables else include.append(model) for model in models]
    return include, exclude
