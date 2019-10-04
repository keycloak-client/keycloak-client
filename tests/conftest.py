# -*- coding: utf-8 -*-
import os

import pytest

from flask import Flask, Response
from keycloak import KeycloakClient
from keycloak.extensions.flask import Authentication


def _keycloak_client():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, "keycloak.json")
    return KeycloakClient(config_file=config_file)


app = Flask(__name__)
keycloak_client = _keycloak_client()
Authentication(app, keycloak_client)


@app.route("/")
def home():
    return Response("home")


@pytest.fixture()
def keycloak_client():
    """ fixture for keycloak client """
    return _keycloak_client()


@pytest.fixture()
def flask_client():
    """ fixture for flask client """
    yield app.test_client()
