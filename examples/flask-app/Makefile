all: install run

install:
	pip install -r requirements.txt

run:
	python app.py

resource:
	FLASK_APP=app.py flask register-resources
