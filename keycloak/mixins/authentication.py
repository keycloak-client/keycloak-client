#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with authentication """

import urllib
import uuid
import requests


class AuthenticationMixin:
    """
    This class includes the methods to interact with the authentication flow
    """

    def authentication_url(self, scopes=('openid',)):
        """
        Method which builds the login url for keycloak

        Args:
            scopes (tuple): list of scopes

        Returns:
            str
        """
        self.log.info('Constructing authentication url')
        arguments = urllib.parse.urlencode({
            'state': uuid.uuid4(),
            'client_id': self.config.client_id,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'redirect_uri': self.config.redirect_uri
        })
        return self.config.authorization_endpoint + '?' + arguments

    def authentication_callback(self, code):
        """
        Method to retrieve access_token, refresh_token and id_token

        Args:
            code (str): authentication code received in the callback

        Returns:
            access_token (str)
            refresh_token (str)
            id_token (str)
        """

        # prepare request payload
        payload = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'client_secret': self.config.client_secret,
        }

        # retrieve tokens from keycloak server
        try:
            self.log.info('Retrieving AAT from keycloak server')
            response = requests.post(self.config.token_endpoint, data=payload)
            response.raise_for_status()
        except Exception as ex:
            self.log.exception('Failed to retrieve AAT from keycloak server')
            raise ex

        return response.json()
