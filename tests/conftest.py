# -*- coding: utf-8 -*-
import os
import json

import pytest
from keycloak import Client
from keycloak.config import (
    config,
    ClientConfiguration,
    OpenIdConfiguration,
    Uma2Configuration,
)


here = os.path.dirname(os.path.realpath(__file__))


def read_json(file, cls=None):
    path = os.path.join(here, "data", file)
    with open(path, "r") as f:
        data = json.loads(f.read())
        return cls(**data) if cls else data


client = read_json("client.json", ClientConfiguration)
openid = read_json("openid.json", OpenIdConfiguration)
uma2 = read_json("uma2.json", Uma2Configuration)
certs = read_json("certs.json")


@pytest.fixture(autouse=True)
def configs(monkeypatch):
    monkeypatch.setattr("keycloak.config.KeycloakConfiguration.client", client)
    monkeypatch.setattr("keycloak.config.KeycloakConfiguration.openid", openid)
    monkeypatch.setattr("keycloak.config.KeycloakConfiguration.uma2", uma2)
    monkeypatch.setattr("keycloak.mixins.jwt.JWTMixin._certs", certs)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture()
def kc_config(monkeypatch):
    yield config


@pytest.fixture()
def kc_client(monkeypatch):
    yield Client()
