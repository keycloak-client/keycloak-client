#! -*- coding: utf-8 -*-
import os

import pytest

from keycloak import KeycloakClient


@pytest.fixture
def keycloak_client():
    """ fixture for keycloak client """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, 'keycloak.json')
    return KeycloakClient(config_file=config_file)
