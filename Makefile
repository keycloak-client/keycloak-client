.PHONY: clean install docs _build build upload

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf build dist || true

install:
	pip install -e .

docs:
	pip install sphinx sphinx_rtd_theme

_build:
	python setup.py sdist bdist_wheel

build: clean _build

upload:
	python -m twine upload dist/*

all: clean install build upload
