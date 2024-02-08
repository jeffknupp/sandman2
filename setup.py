"""Setup script for sandman2."""
from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import re

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Return multiple read calls to different readable objects as a single
    string."""
   
    return codecs.open(os.path.join(HERE, *parts), 'r', encoding='utf-8').read()

LONG_DESCRIPTION = read('README.rst')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--strict',
            '--verbose',
            '--tb=long',
            'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='sandman2',
    version='1.2.2',
    url='http://github.com/jeffknupp/sandman2/',
    license='Apache Software License',
    author='Jeff Knupp',
    tests_require=['pytest', 'pytest-cov', 'pytest-flask'],
    install_requires=[
        'itsdangerous==2.0.1',  # old json
        'jinja2==3.0.3',  # jinja2 < 3.1.0 for jinja2.escape - alternative newer flask
        'Werkzeug==1.0.1',
        'Flask==1.1.2',
        'Flask-SQLAlchemy==2.4.4',
        'SQLAlchemy==1.3.20',
        'Flask-Admin>=1.5.37',
        'Flask-HTTPAuth>=3.2.4',
        'colorama',
        ],
    cmdclass={'test': PyTest},
    author_email='jeff@jeffknupp.com',
    description='Automated REST APIs for legacy (existing) databases',
    long_description=LONG_DESCRIPTION,
    entry_points={
        'console_scripts': [
            'sandman2ctl = sandman2.__main__:main',
            ],
        },
    packages=['sandman2'],
    include_package_data=True,
    platforms='any',
    test_suite='tests.test_sandman2',
    zip_safe=False,
    package_data={'sandman2': ['templates/**.html']},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
)
