.PHONY: clean _install_dep _dev_dep install _pytest _lint test _build build upload importanize all

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf build dist || true

_install_dep:
	pip install -e .

_dev_dep:
	pip install -r dev.txt

install: _install_dep _dev_dep

_pytest:
	pytest --cov=keycloak tests/ --cov-fail-under=80

_lint:
	python linter.py --fail-under=9 keycloak

test: _lint _pytest

_build:
	python setup.py sdist bdist_wheel

build: clean _build

upload:
	python -m twine upload dist/*

importanize:
	find keycloak -name '*.py' | xargs importanize
	find tests -name '*.py' | xargs importanize

all: clean install test build upload
