.PHONY: clean install lint mypy test keycloak

clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +

install:
	pip install poetry --upgrade
	poetry install --extras "docs extensions"

lint:
	poetry run black keycloak tests
	poetry run isort --profile=black keycloak tests

mypy:
	poetry run mypy --install-types --non-interactive keycloak

test:
	poetry run black --check keycloak tests 
	poetry run isort --profile=black --check keycloak tests
	poetry run pytest tests --exitfirst

keycloak:
	docker run --detach --name keycloak --env KEYCLOAK_USER=admin --env KEYCLOAK_PASSWORD=admin --publish 8080:8080 --publish 8081:8081 jboss/keycloak
