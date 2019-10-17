# -*- coding: utf-8 -*-
import os
import json

import pytest

from flask import Flask

from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient


from keycloak import Client as KeycloakClient
from keycloak.config import config, Client, OpenId, Uma2
from keycloak.extensions.flask import Authentication as FlaskAuthentication
from keycloak.extensions.starlette import Authentication as StarletteAuthentication


here = os.path.dirname(os.path.realpath(__file__))


def read_json(file, cls=None):
    path = os.path.join(here, "data", file)
    with open(path, "r") as f:
        data = json.loads(f.read())
        return cls(**data) if cls else data


client = read_json("client.json", Client)
openid = read_json("openid.json", OpenId)
uma2 = read_json("uma2.json", Uma2)
certs = read_json("certs.json")


@pytest.fixture(autouse=True)
def configs(monkeypatch):
    monkeypatch.setattr("keycloak.config.Config.client", client)
    monkeypatch.setattr("keycloak.config.Config.openid", openid)
    monkeypatch.setattr("keycloak.config.Config.uma2", uma2)
    monkeypatch.setattr("keycloak.mixins.jwt.JWTMixin._certs", certs)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture()
def kc_config(monkeypatch):
    yield config


@pytest.fixture()
def kc_client(monkeypatch):
    yield KeycloakClient()


flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = "secret0123456789"
FlaskAuthentication(flask_app)


@flask_app.route("/howdy")
def flask_howdy():
    return "Howdy!"


@pytest.fixture()
def flask_client():
    yield flask_app.test_client()


starlette_app = Starlette()
starlette_app.add_middleware(SessionMiddleware, secret_key="key0123456789")
starlette_app.add_middleware(StarletteAuthentication)


@starlette_app.route("/howdy")
def starlette_howdy():
    return PlainTextResponse("Howdy!")


@pytest.fixture()
def starlette_client():
    yield TestClient(starlette_app)
