# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict
from dataclasses import dataclass, fields
from functools import lru_cache

import yaml
import requests
from cached_property import cached_property

from .constants import EnvVar, Defaults, FileMode, Logger
from .utils import Singleton


log = logging.getLogger(Logger.name)


class DataClassMixin:
    def __init__(self, **kwargs: Dict):
        attrs = [x.name for x in fields(self)]
        for key, val in kwargs.items():
            if key in attrs:
                setattr(self, key, val)


@dataclass(init=False)
class Client(DataClassMixin):
    realm: str
    hostname: str
    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass(init=False)
class OpenId(DataClassMixin):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    end_session_endpoint: str
    jwks_uri: str
    introspection_endpoint: str


@dataclass(init=False)
class Uma2(DataClassMixin):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    end_session_endpoint: str
    jwks_uri: str
    resource_registration_endpoint: str
    permission_endpoint: str
    policy_endpoint: str
    introspection_endpoint: str


class Config(metaclass=Singleton):
    @property
    def settings_file(self) -> str:
        log.debug("Lookup settings file in the env vars")
        return os.getenv(EnvVar.keycloak_settings, Defaults.keycloak_settings)

    @cached_property
    def client(self) -> Client:
        log.debug("Loading client config from the settings file")
        with open(self.settings_file, FileMode.read_only) as stream:
            data = yaml.safe_load(stream)
            return Client(**data)

    @property
    def openid_endpoint(self) -> str:
        return (
            self.client.hostname
            + "/auth/realms/"
            + self.client.realm
            + "/.well-known/openid-configuration"
        )

    @cached_property
    def openid(self) -> OpenId:
        log.debug("Loading openid config using well-known endpoint")
        response = requests.get(self.openid_endpoint)
        response.raise_for_status()
        data = response.json()
        return OpenId(**data)

    @property
    def uma_endpoint(self) -> str:
        return (
            self.client.hostname
            + "/auth/realms/"
            + self.client.realm
            + "/.well-known/uma2-configuration"
        )

    @cached_property
    def uma2(self) -> Uma2:
        log.debug("Loading uma2 config using well-known endpoint")
        response = requests.get(self.uma_endpoint)
        response.raise_for_status()
        data = response.json()
        return Uma2(**data)


config: Config = Config()
