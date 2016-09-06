"""Shared fixtures for test modules."""
import os
import importlib
import inspect
import shutil
import sys

sys.path.insert(0, os.path.abspath('.'))

import pytest

from sandman2 import get_app, db



@pytest.yield_fixture(scope='function')
def app(request):
    """Yield the application instance."""
    database = getattr(request.module, 'database', 'db.sqlite3')
    read_only = getattr(request.module, 'read_only', False)
    exclude_tables = getattr(request.module, 'exclude_tables', None)
    test_database_path = os.path.join('tests', 'data', 'test_db.sqlite3')
    pristine_database_path = os.path.join('tests', 'data', database)

    shutil.copy(pristine_database_path, test_database_path)

    model_module = getattr(request.module, 'model_module', None)
    user_models = []
    if model_module:
        module = importlib.import_module(model_module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if name not in ('Model', 'AutomapModel'):
                    user_models.append(obj)

    application = get_app(
        'sqlite+pysqlite:///{}'.format(
            test_database_path),
        user_models=user_models,
        exclude_tables=exclude_tables,
        read_only=read_only)
    application.testing = True

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()
    os.unlink(test_database_path)
