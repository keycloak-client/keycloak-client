.PHONY: clean install lint test keycloak

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
	pip install poetry && poetry install
	mypy --install-types --non-interactive keycloak

lint:
	black keycloak tests 
	isort --profile=black keycloak tests
	mypy --ignore-missing-imports --disallow-untyped-defs keycloak

test:
	black --check keycloak tests 
	isort --profile=black --check keycloak tests
	pytest tests

keycloak:
	docker run --detach --name keycloak --env KEYCLOAK_USER=admin --env KEYCLOAK_PASSWORD=admin --publish 8080:8080 --publish 8081:8081 jboss/keycloak
