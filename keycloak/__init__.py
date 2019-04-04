#! -*- coding: utf-8 -*-

""" keycloak module """

import logging
from logging.handlers import RotatingFileHandler

from .client import KeycloakClient


# define log handler
handler = RotatingFileHandler(filename='/tmp/keycloak-client.log', maxBytes=10000000, backupCount=5)


# define logger
logger = logging.getLogger('keycloak-client')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
