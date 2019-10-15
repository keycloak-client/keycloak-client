# -*- coding: utf-8 -*-
from .mixins.authentication import AuthenticationMixin
from .mixins.authorization import AuthorizationMixin
from .mixins.jwt import JWTMixin
from .utils import Singleton


class Client(AuthenticationMixin, AuthorizationMixin, JWTMixin, metaclass=Singleton):
    pass


__all__ = ["Client"]
