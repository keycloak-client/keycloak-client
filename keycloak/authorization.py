#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with authorization """

import base64

import requests
from cached_property import cached_property


class AuthorizationMixin:
    """
    This class include methods that interact with the authorization api
    For details see https://www.keycloak.org/docs/5.0/authorization_services/index.html
    """

    @cached_property
    def basic_authorization_header(self):
        """
        Method to prepare the authorization header

        Returns:
            str
        """

        # construct authorization string
        authorization = '{}:{}'.format(self.config.client_id, self.config.client_secret)

        # convert to bytes
        authorization = bytes(authorization, 'utf-8')

        # perform base64 encoding
        authorization = base64.b64encode(authorization)

        # convert to str
        authorization = authorization.decode('utf-8')

        return 'Basic {}'.format(authorization)

    @cached_property
    def permission_ticket(self):
        """ Method to generate permission ticket """
        return {
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': self.config.client_id
        }

    def retrieve_rpt(self, aat=None, permission_ticket=None):
        """
        Method to fetch the request party token (RPT)

        Args:
            aat (str): authorization api token
        """
        # validate inputs
        try:
            assert isinstance(aat, str)
        except Exception as ex:
            self.log.error('Invalid AAT')
            raise ex

        # handle default value for permission ticket
        if permission_ticket is None:
            permission_ticket = self.permission_ticket

        # prepare headers
        headers = {
            'Authorization': 'Bearer {}'.format(aat)
        }

        # fetch RPT token
        try:
            response = requests.post(
                self.config.token_endpoint,
                data=self.permission_ticket,
                headers=headers
            )
            response.raise_for_status()
        except Exception as ex:
            self.log.exception('Failed to retrieve RPT from keycloak server')
            raise ex

        return response.json()

    def validate_rpt(self, rpt):
        """
        Method to introspect and validate the request party token (RPT)

        Args:
             rpt (str): RPT received
        """

        try:
            assert isinstance(rpt, str)
        except Exception as ex:
            self.log.error('Invalid RPT')
            raise ex

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
        try:
            response = requests.post(
                self.config.introspection_endpoint,
                data=payload,
                headers=headers
            )
            response.raise_for_status()
        except Exception as ex:
            self.log.exception('Failed to validate RPT from keycloak server')
            raise ex

        return response.json()
