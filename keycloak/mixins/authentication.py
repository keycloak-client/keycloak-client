#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with authentication """

import urllib
import uuid

import requests
from cached_property import cached_property

from ..exceptions import InvalidAuthorizationCode


class AuthenticationMixin:
    """
    This class includes the methods to interact with the authentication flow
    """

    @cached_property
    def authentication_url(self):
        """
        Method which builds the login url for keycloak

        Returns:
            str
        """
        self.log.info('Constructing authentication url')
        arguments = urllib.parse.urlencode({
            'state': uuid.uuid4(),
            'client_id': self.config.client_id,
            'response_type': 'code',
            'scope': 'openid email profile user_roles',
            'redirect_uri': self.config.redirect_uri
        })
        return self.config.authorization_endpoint + '?' + arguments

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
            self.log.error('Invalid authorization code')
            raise InvalidAuthorizationCode

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
