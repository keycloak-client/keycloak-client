# -*- coding: utf-8 -*-
import os

import yaml
import requests

from .constants import EnvVar, Defaults, FileMode
from .utils import Singleton


class Configuration(metaclass=Singleton):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


class ClientConfiguration(Configuration):
    realm = None
    hostname = None
    client_id = None
    client_secret = None
    redirect_uri = None


class OpenIdConfiguration(Configuration):
    issuer = None
    authorization_endpoint = None
    token_endpoint = None
    userinfo_endpoint = None
    end_session_endpoint = None
    jwks_uri = None
    introspection_endpoint = None


class Uma2Configuration(Configuration):
    issuer = None
    authorization_endpoint = None
    token_endpoint = None
    end_session_endpoint = None
    jwks_uri = None
    resource_registration_endpoint = None
    permission_endpoint = None
    policy_endpoint = None
    introspection_endpoint = None


class KeycloakConfiguration(Configuration):
    client = None
    uma2 = None
    openid = None

    @property
    def settings_file(self) -> str:
        return os.getenv(EnvVar.keycloak_settings, Defaults.keycloak_settings)

    def load_client_configuration(self):
        with open(self.settings_file, FileMode.read_only) as stream:
            data = yaml.safe_load(stream)
            self.client = ClientConfiguration(**data)

    @property
    def openid_wellknown_endpoint(self) -> str:
        return f"{self.client.hostname}/auth/realms/{self.client.realm}/.well-known/openid-configuration"

    @property
    def uma_wellknown_endpoint(self) -> str:
        return f"{self.client.hostname}/auth/realms/{self.client.realm}/.well-known/uma2-configuration"

    def load_openid_configuration(self):
        response = requests.get(self.openid_wellknown_endpoint)
        response.raise_for_status()
        data = response.json()
        self.openid = OpenIdConfiguration(**data)

    def load_uma2_configuration(self):
        response = requests.get(self.uma_wellknown_endpoint)
        response.raise_for_status()
        data = response.json()
        self.uma2 = Uma2Configuration(**data)

    def __init__(self):
        self.load_client_configuration()
        self.load_openid_configuration()
        self.load_uma2_configuration()


config = KeycloakConfiguration()
