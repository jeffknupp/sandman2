"""Shared fixtures for test modules."""
import os
import importlib
import inspect
import shutil
import sys

sys.path.insert(0, os.path.abspath('.'))

import pytest

from sandman2 import get_app, db


TEST_DATABASE_PATH = os.path.join('tests', 'data', 'test_db.sqlite3')
PRISTINE_DATABASE_PATH = os.path.join('tests', 'data', 'db.sqlite3')

shutil.copy(PRISTINE_DATABASE_PATH, TEST_DATABASE_PATH)


@pytest.yield_fixture(scope='function')
def app():
    """Yield the application instance."""
    if os.path.exists(TEST_DATABASE_PATH):
        os.unlink(TEST_DATABASE_PATH)
    shutil.copy(PRISTINE_DATABASE_PATH, TEST_DATABASE_PATH)

    APPLICATION = get_app('sqlite+pysqlite:///tests/data/test_db.sqlite3')
    APPLICATION.testing = True

    yield APPLICATION

    with APPLICATION.app_context():
        db.session.remove()
        db.drop_all()
    os.unlink(TEST_DATABASE_PATH)


#@pytest.yield_fixture(scope='function')
#def user_app(request):
#    """Yield the application instance with the given user-defined models."""
#    model_module = getattr(request.module, 'model_module')
#    module = importlib.import_module(model_module)
#    user_models = []
#    for obj in inspect.getmembers(module):
#        if inspect.isclass(obj):
#            user_models.append(obj)

