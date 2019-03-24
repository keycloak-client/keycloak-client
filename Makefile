.PHONY: clean install build upload

clean:
	find . -type f -name '*.pyc' -delete

install:
	pip install -e .

build:
	python setup.py sdist bdist_wheel

upload:
	python -m twine upload dist/*

all: clean install build upload
