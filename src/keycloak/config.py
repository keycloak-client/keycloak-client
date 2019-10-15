# -*- coding: utf-8 -*-
import os
from typing import Dict

import yaml
import requests

from .constants import EnvVar, Defaults, FileMode
from .utils import Singleton


class Configuration(metaclass=Singleton):
    def __init__(self, **kwargs: Dict):
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


class ClientConfiguration(Configuration):
    realm: str = None  # type: ignore
    hostname: str = None  # type: ignore
    client_id: str = None  # type: ignore
    client_secret: str = None  # type: ignore
    redirect_uri: str = None  # type: ignore


class OpenIdConfiguration(Configuration):
    issuer: str = None  # type: ignore
    authorization_endpoint: str = None  # type: ignore
    token_endpoint: str = None  # type: ignore
    userinfo_endpoint: str = None  # type: ignore
    end_session_endpoint: str = None  # type: ignore
    jwks_uri: str = None  # type: ignore
    introspection_endpoint: str = None  # type: ignore


class Uma2Configuration(Configuration):
    issuer: str = None  # type: ignore
    authorization_endpoint: str = None  # type: ignore
    token_endpoint: str = None  # type: ignore
    end_session_endpoint: str = None  # type: ignore
    jwks_uri: str = None  # type: ignore
    resource_registration_endpoint: str = None  # type: ignore
    permission_endpoint: str = None  # type: ignore
    policy_endpoint: str = None  # type: ignore
    introspection_endpoint: str = None  # type: ignore


class KeycloakConfiguration(Configuration):
    _client: ClientConfiguration = None  # type: ignore
    _openid: OpenIdConfiguration = None  # type: ignore
    _uma2: Uma2Configuration = None  # type: ignore

    @property
    def settings_file(self) -> str:
        return os.getenv(EnvVar.keycloak_settings, Defaults.keycloak_settings)

    def load_client(self) -> None:
        with open(self.settings_file, FileMode.read_only) as stream:
            data = yaml.safe_load(stream)
            self._client = ClientConfiguration(**data)

    @property
    def client(self) -> ClientConfiguration:
        if self._client is None:
            self.load_client()
        return self._client

    @property
    def openid_wellknown_endpoint(self) -> str:
        return f"{self.client.hostname}/auth/realms/{self.client.realm}/.well-known/openid-configuration"

    def load_openid(self) -> None:
        response = requests.get(self.openid_wellknown_endpoint)
        response.raise_for_status()
        data = response.json()
        self._openid = OpenIdConfiguration(**data)

    @property
    def openid(self) -> OpenIdConfiguration:
        if self._openid is None:
            self.load_openid()
        return self._openid

    @property
    def uma_wellknown_endpoint(self) -> str:
        return f"{self.client.hostname}/auth/realms/{self.client.realm}/.well-known/uma2-configuration"

    def load_uma2(self) -> None:
        response = requests.get(self.uma_wellknown_endpoint)
        response.raise_for_status()
        data = response.json()
        self._uma2 = Uma2Configuration(**data)

    @property
    def uma2(self) -> Uma2Configuration:
        if self._uma2 is None:
            self.load_uma2()
        return self._uma2


config: KeycloakConfiguration = KeycloakConfiguration()
