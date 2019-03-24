#! -*- coding: utf-8 -*-
import os
import json
import uuid
import base64
import urllib
import requests


class KeycloakClient(object):

    def __init__(self, config_file=None):
        """
        Method to initialize keycloak client

        Args:
            config_file(str): path to the keycloak config file
        """

        # default config file to keycloak.json
        config_file = 'keycloak.json' if config_file is None else config_file

        # validate config file
        if os.path.isfile(config_file) == False:
            raise ValueError('Unable to find the config file in the given path')

        # read config file
        with open(config_file, 'r') as file_descriptor:
            file_content = file_descriptor.read()

        # validate file is json loadable
        try:
            config = json.loads(file_content)
        except json.decoder.JSONDecodeError:
            raise ValueError('Invalid json file')

        # validate whether the required configs are present or not
        assert 'client_id' in config
        assert 'client_secret' in config
        assert 'redirect_uri' in config
        assert 'authorization_endpoint' in config
        assert 'token_endpoint' in config
        assert 'introspection_endpoint' in config

        # load config to object
        self.config = config


    @property
    def login_url(self):
        """
        Method which builds the login url for keycloak

        Returns:
            str
        """
        arguments = urllib.parse.urlencode({
            'state': uuid.uuid4(),
            'client_id': self.config['client_id'],
            'response_type': 'code',
            'scope': 'openid email profile user_roles',
            'redirect_uri': self.config['redirect_uri']
        })
        return self.config['authorization_endpoint'] + '?' + arguments

    @staticmethod
    def fix_padding(encoded_data):
        """
        Method to correct padding for base64 encoding

        Args:
            encoded_data (str): base64 encoded string/data

        Returns:
            str
        """
        required_padding = len(encoded_data) % 4
        return encoded_data + ('=' * required_padding)

    def retrieve_tokens(self, code=None):
        """
        Method to retrieve access_token, refresh_token and id_token

        Args:
            code (str): authentication code received in the callback

        Returns:
            access_token (str)
            refresh_token (str)
            id_token (str)
        """

        # validate code
        if code is None:
            raise ValueError('Invalid code')

        # prepare request payload
        payload = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.config['client_id'],
            'redirect_uri': self.config['redirect_uri'],
            'client_secret': self.config['client_secret'],
        }

        # retrieve tokens from keycloak server
        response = requests.post(self.config['token_endpoint'], data=payload)
        response.raise_for_status()

        # parse tokens
        response = response.json()
        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        id_token = response.get('id_token')

        # fix base64 padding
        access_token = KeycloakClient.fix_padding(access_token)
        refresh_token = KeycloakClient.fix_padding(refresh_token)
        id_token = self.fix_padding(id_token)

        return access_token, refresh_token, id_token

    @staticmethod
    def get_access_token_info(access_token):
        """
        Method to decode the given access token

        Args:
             access_token (str): access token received
        """

        # parse token segments
        info, access_token, hash = access_token.split('.')

        # fix padding
        access_token = KeycloakClient.fix_padding(access_token)

        # decode base64 encoded string
        access_token = base64.b64decode(access_token)

        # convert json to dict
        return json.loads(access_token)

    @staticmethod
    def get_id_token_info(id_token):
        """
        Method to decode the given access token

        Args:
             id_token (str): id token received
        """

        # parse token segments
        info, id_token, hash = id_token.split('.')

        # fix padding
        id_token = KeycloakClient.fix_padding(id_token)

        # decode base64 encoded string
        id_token = base64.b64decode(id_token)

        # convert json to dict
        return json.loads(id_token)
