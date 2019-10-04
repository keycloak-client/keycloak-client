# -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with configurations """

import json
import os

import requests


class Configuration:
    """ keycloak configuration """

    # from config file
    realm = None
    hostname = None
    client_id = None
    client_secret = None
    redirect_uri = None

    # from .well-known endpoint
    issuer = None
    authorization_endpoint = None
    token_endpoint = None
    token_introspection_endpoint = None
    end_session_endpoint = None
    jwks_uri = None
    grant_types_supported = None
    response_types_supported = None
    response_modes_supported = None
    registration_endpoint = None
    token_endpoint_auth_methods_supported = None
    token_endpoint_auth_signing_alg_values_supported = None
    scopes_supported = None
    resource_registration_endpoint = None
    permission_endpoint = None
    policy_endpoint = None
    introspection_endpoint = None

    def __init__(self, config_file=None):
        """
        initialize keycloak configuration

        Args:
            config_file(str): path to the keycloak config file
        """

        # default config file to keycloak.json
        config_file = "keycloak.json" if config_file is None else config_file

        # validate config file
        if not os.path.isfile(config_file):
            raise ValueError(
                "Unable to find the config file in the given path %s", config_file
            )

        # read config file
        with open(config_file, "r") as file_descriptor:
            file_content = file_descriptor.read()

        # validate file is json loadable
        try:
            config = json.loads(file_content)
        except json.decoder.JSONDecodeError:
            raise ValueError("Invalid json file")

        # set attributes
        for key, val in config.items():
            setattr(self, key, val)

        # fetch urls using well-known url
        well_known = (
            f"{self.hostname}/auth/realms/{self.realm}/.well-known/uma2-configuration"
        )
        response = requests.get(well_known)
        response.raise_for_status()

        # set attributes
        for key, val in response.json().items():
            setattr(self, key, val)
