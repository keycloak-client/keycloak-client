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
        assert 'authentication_endpoint' in config
        assert 'token_endpoint' in config
        assert 'introspection_endpoint' in config

        # load config to object
        self.config = config

    @property
    def basic_authorization_header(self):
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

    @property
    def authentication_url(self):
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
        return self.config['authentication_endpoint'] + '?' + arguments

    def authentication_callback(self, code=None):
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

        return response.json()

    def retrieve_rpt(self, access_token):
        """
        Method to fetch the RPT

        Args:
            access_token (str): access token received
        """

        # prepare payload
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': self.config['client_id']
        }

        # prepare headers
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }

        # fetch RPT token
        response = requests.post(self.config['token_endpoint'], data=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    def validate_rpt(self, access_token):
        """
        Method to introspect and validate access token

        Args:
             access_token (str): access token received
        """

        # prepare payload
        payload = {
            'token_type_hint': 'requesting_party_token',
            'token': access_token
        }

        # prepare headers
        headers = {
            'Authorization': self.basic_authorization_header
        }

        # introspect token
        response = requests.post(self.config['introspection_endpoint'], data=payload, headers=headers)
        response.raise_for_status()

        return response.json()
