#! -*- coding: utf-8 -*-

""" keycloak client created out of different mixins """
import logging

from .config import Configuration
from .log import get_logger
from .mixins.authentication import AuthenticationMixin
from .mixins.authorization import AuthorizationMixin
from .mixins.resource import ResourceMixin
from .mixins.token import JwtMixin


# pylint: disable=line-too-long
class KeycloakClient(AuthenticationMixin, AuthorizationMixin, ResourceMixin, JwtMixin):
    """ keycloak client """

    def __init__(self, config_file=None, log_dir=None, log_level=logging.DEBUG):
        """
        Method to initialize keycloak client

        Args:
            config_file(str): path to the keycloak config file
        """
        self.log = get_logger(log_dir, log_level)
        self.config = Configuration(config_file=config_file)
