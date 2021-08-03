# -*- coding: utf-8 -*-

from keycloak.core.asynchronous.authentication import AsyncAuthenticationMixin
from keycloak.core.asynchronous.authorization import AsyncAuthorizationMixin
from keycloak.core.asynchronous.resource import AsyncResourceMixin
from keycloak.core.asynchronous.token import AsyncTokenMixin
from keycloak.core.authentication import AuthenticationMixin
from keycloak.core.authorization import AuthorizationMixin
from keycloak.core.resource import ResourceMixin
from keycloak.core.token import TokenMixin
from keycloak.utils import Singleton


class Client(
    AuthenticationMixin,
    AuthorizationMixin,
    TokenMixin,
    ResourceMixin,
    metaclass=Singleton,
):
    """
    Python client to interact with the rest APIs provided by the keycloak server
    """

    def __init__(
        self,
        callback_uri: str = "http://localhost/kc/callback",
        username: str = None,
        password: str = None,
    ) -> None:
        self.callback_uri = callback_uri
        self.username = username
        self.password = password


class AsyncClient(
    AsyncAuthenticationMixin,
    AsyncAuthorizationMixin,
    AsyncTokenMixin,
    AsyncResourceMixin,
    metaclass=Singleton,
):
    def __init__(
        self,
        callback_uri: str = "http://localhost/kc/callback",
        username: str = None,
        password: str = None,
    ) -> None:
        self.callback_uri = callback_uri
        self.username = username
        self.password = password


__all__ = ["Client", "AsyncClient"]
