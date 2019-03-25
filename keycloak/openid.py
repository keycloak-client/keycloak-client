#! -*- coding: utf-8 -*-
import uuid
import urllib
import requests


class OpenIdMixin(object):
    """
    This class includes the methods to interact with the openid/authentication flow
    """

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
