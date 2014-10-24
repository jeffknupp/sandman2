sed -i -e "s/__version__ = '.*'/__version__ = '$1'/g" sandman2/__init__.py
python setup.py develop
make docs
cd docs && make html && cd ..
git commit docs sandman2/__init__.py -m "Update to version v$1"
python setup.py sdist bdist_wheel upload -r pypi
python setup.py upload_docs -r pypi
