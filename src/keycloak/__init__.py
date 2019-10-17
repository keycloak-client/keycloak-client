# -*- coding: utf-8 -*-
from typing import Tuple, Dict

from .mixins.authentication import AuthenticationMixin
from .mixins.authorization import AuthorizationMixin
from .mixins.jwt import JWTMixin
from .utils import Singleton


class Client(AuthenticationMixin, AuthorizationMixin, JWTMixin, metaclass=Singleton):
    def __init__(self, redirect_uri: str):
        self.redirect_uri = redirect_uri


__all__ = ["Client"]
