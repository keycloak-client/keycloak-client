# -*- coding: utf-8 -*-
import logging

import requests

from .log import logger  # register logger
from .mixins.authentication import AuthenticationMixin
from .mixins.authorization import AuthorizationMixin
from .mixins.token import TokenMixin
from .mixins.resource import ResourceMixin
from .utils import Singleton


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


__all__ = ["Client"]
