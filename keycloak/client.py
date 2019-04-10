#! -*- coding: utf-8 -*-

""" keycloak client created out of different mixins """

from .authentication import AuthenticationMixin
from .authorization import AuthorizationMixin
from .config import Configuration
from .logging import LoggingMixin
from .resource import ResourceMixin
from .token import JwtMixin


# pylint: disable=line-too-long
class KeycloakClient(LoggingMixin, JwtMixin, AuthenticationMixin, AuthorizationMixin, ResourceMixin):
    """ keycloak client """

    def __init__(self, config_file=None, **kwargs):
        """
        Method to initialize keycloak client

        Args:
            config_file(str): path to the keycloak config file
        """
        self.config = Configuration(config_file=config_file)
        super(KeycloakClient, self).__init__(**kwargs)
