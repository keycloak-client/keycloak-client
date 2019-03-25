.PHONY: clean install test  _build build upload

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf build dist || true

install:
	pip install -e .
	pip install sphinx sphinx_rtd_theme pytest==4.3.1 pytest-cov==2.6.1 codecov==2.0.15

test:
	pytest --cov=keycloak tests/

_build:
	python setup.py sdist bdist_wheel

build: clean _build

upload:
	python -m twine upload dist/*

all: clean install build upload
