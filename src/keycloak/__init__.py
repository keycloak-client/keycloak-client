# -*- coding: utf-8 -*-
import logging

import requests

from .log import logger  # this import is to register logger
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
    def __init__(
        self,
        redirect_uri: str = "http://localhost/kc/callback",
        username: str = None,
        password: str = None,
    ):
        self.redirect_uri = redirect_uri
        self.username = username
        self.password = password


__all__ = ["Client"]
