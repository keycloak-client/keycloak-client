# -*- coding: utf-8 -*-
import pytest
from flask import Flask, Response

from keycloak import Client, config
from keycloak.extensions.flask import Authentication


app = Flask(__name__)
kc = Client()
Authentication(app, kc)


@app.route("/")
def home():
    return Response("home")


@pytest.fixture()
def kc_config():
    yield config


@pytest.fixture()
def kc_client():
    yield Client()


@pytest.fixture()
def flask_client():
    yield app.test_client()
