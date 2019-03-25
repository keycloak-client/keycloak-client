#! -*- coding: utf-8 -*-
import base64
import requests


class AuthorizationMixin(object):
    """
    This class include methods that interact with the authorization api
    For details see https://www.keycloak.org/docs/5.0/authorization_services/index.html
    """

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

    def retrieve_rpt(self, aat):
        """
        Method to fetch the request party token (RPT)

        Args:
            aat (str): authorization api token
        """

        # prepare payload
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': self.config['client_id']
        }

        # prepare headers
        headers = {
            'Authorization': 'Bearer {}'.format(aat)
        }

        # fetch RPT token
        response = requests.post(self.config['token_endpoint'], data=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    def validate_rpt(self, rpt):
        """
        Method to introspect and validate the request party token (RPT)

        Args:
             rpt (str): RPT received
        """

        # prepare payload
        payload = {
            'token_type_hint': 'requesting_party_token',
            'token': rpt
        }

        # prepare headers
        headers = {
            'Authorization': self.basic_authorization_header
        }

        # introspect token
        response = requests.post(self.config['introspection_endpoint'], data=payload, headers=headers)
        response.raise_for_status()

        return response.json()
