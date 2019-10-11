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
	pip install pre-commit && pre-commit install

test:
	python setup.py pytest

build: clean
	python setup.py sdist bdist_wheel

upload:
	twine upload -r pypi dist/*

all: clean install test build upload
