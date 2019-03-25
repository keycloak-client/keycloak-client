#! -*- coding: utf-8 -*-
import os
import json
import uuid
import base64
import urllib
import requests
from datetime import datetime


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
        if not os.path.isfile(config_file):
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

    @staticmethod
    def get_user_info(id_token):
        """
        Method to parse user info from the id token

        Args:
            id_token (str): id token received

        Returns:
            dict
        """
        id_token = KeycloakClient.get_id_token_info(id_token)
        return {
            'id': id_token['sub'],
            'name': id_token['name'],
            'email': id_token['email'],
            'expiration_time': datetime.fromtimestamp(id_token['exp']),
            'authentication_time': datetime.fromtimestamp(id_token['auth_time']),
        }

    def get_access_info(self, access_token):
        """
        Method to parse access info from the access token

        Args:
             access_token (str): access token received

        Returns:
            dict
        """
        access_token = KeycloakClient.get_access_token_info(access_token)
        return access_token['resource_access'].get(self.config['client_id'], {'roles': []})

    def get_info(self, access_token, id_token):
        """
        Method to parse information out of the tokens

        Args:
            access_token (str): access token received
            id_token (str): id token received

        Returns:
            dict
        """
        user_info = KeycloakClient.get_user_info(id_token)
        access_info = self.get_access_info(access_token)
        user_info.update(access_info)
        return user_info

    def get_authorization_header(self):
        """
        Method to prepare the authorization header

        Returns:
            str
        """

        # construct authorization string
        authorization = '{}:{}'.format(self.config['client_id'], self.config['client_secret'])

        # convert to bytes
        authorization = bytes(authorization, 'utf-8')

        # perform base64 encoding
        authorization = base64.b64encode(authorization)

        # convert to str
        authorization = authorization.decode('utf-8')

        return 'Basic {}'.format(authorization)

    def validate_access_token(self, access_token):
        """
        Method to introspect and validate access token

        Args:
             access_token (str): access token received
        """
        payload = {
            'token_type_hint': 'access_token',
            'token': access_token
        }
        headers = {
            'Authorization': self.get_authorization_header()
        }
        response = requests.post(self.config['introspection_endpoint'], data=payload, headers=headers)
        response.raise_for_status()
        return response.json()
