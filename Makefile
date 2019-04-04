.PHONY: clean _req_dep _dev_dep install _pytest _lint test _build build upload

clean:
	@echo 'Cleaning junk files'
	find . -type f -name '*.pyc' -delete
	rm -rf build dist || true

_req_dep:
	@echo 'Installaing dependencies required to run the application'
	pip install -e .

_dev_dep:
	@echo 'Installing extra dependencies required for development purpose'
	pip install -r dev.txt

install: _req_dep _dev_dep

_pytest:
	@echo 'Running test cases'
	pytest --cov=keycloak tests/ --cov-fail-under=90
	# pytest --cov=keycloak tests/

_lint:
	@echo 'Running static code analysis'
	python linter.py --fail-under=9 keycloak
	# python linter.py keycloak

test: _lint _pytest

_build:
	@echo 'Creating distribution build'
	python setup.py sdist bdist_wheel

build: clean _build

upload:
	@echo 'Uploading build to the python registry'
	python -m twine upload dist/*

all: clean install test build upload
