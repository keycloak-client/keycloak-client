.PHONY: clean install pytest mypy black test build all keycloak

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name .coverage -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +

install:
	pip install -e .[complete]
	pip install pre-commit mypy black gitchangelog
	pre-commit install

pytest:
	python setup.py pytest

mypy:
	mypy src/keycloak --ignore-missing-imports --disallow-untyped-defs

black:
	black src/keycloak tests --check

test: pytest mypy black

build: clean
	python setup.py sdist bdist_wheel

all: clean install test build

keycloak:
	docker run --detach --name keycloak --env KEYCLOAK_USER=admin --env KEYCLOAK_PASSWORD=admin --publish 8080:8080 --publish 8081:8081 jboss/keycloak

changelog:
	gitchangelog > CHANGES.md
