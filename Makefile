.PHONY: clean install pytest mypy black test build all

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name .coverage -delete
	find . -type d -name .eggs -exec rm -rf {} +
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +

install:
	pip install -e .[extensions]
	pip install pre-commit mypy black
	pre-commit install

pytest:
	python setup.py pytest

mypy:
	mypy src/keycloak --ignore-missing-imports --disallow-untyped-defs

black:
	black src/keycloak tests setup.py --check

test: pytest mypy black

build: clean
	python setup.py sdist bdist_wheel

all: clean install test build
