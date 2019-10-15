.PHONY: clean install test build upload importanize all

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name '.eggs' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	rm -rf build dist || true

install:
	pip install -e .
	pip install pre-commit twine mypy black && pre-commit install

pytest:
	python setup.py pytest

mypy:
	mypy src/keycloak --ignore-missing-imports --disallow-untyped-defs

black:
	black src/keycloak tests setup.py --check

test: pytest mypy black

build: clean
	python setup.py sdist bdist_wheel

upload:
	twine upload -r pypi dist/*

all: clean install test lint build upload
