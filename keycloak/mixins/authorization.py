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

    # pylint: disable=dangerous-default-value
    def retrieve_ticket(self, resources=[]):
        """
        Method to generate permission ticket

        Args:
            resources (list): list of resources fot which ticket needs to be generated

        Raises:
            HTTPError
        """
        # prepare headers
        headers = {
            'Authorization': 'Bearer %s' % self.pat['access_token']
        }

        # retrieve permission ticket
        try:
            self.log.info('Retrieving permission ticket from keycloak server')
            response = requests.post(
                self.config.permission_endpoint,
                json=resources,
                headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to retrieve the permission ticket')
            raise ex

        return response.json()

    def retrieve_rpt(self, aat=None, ticket=None):
        """
        Method to fetch the request party token (RPT)

        Args:
            aat (str): authorization api token
            ticket (str): permission ticket

        Raises:
            InvalidAAT
            InvalidPermissionTicket
            HTTPError
        """
        # prepare payload
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'ticket': ticket,
        }

        # prepare headers
        headers = {
            'Authorization': 'Bearer {}'.format(aat)
        }

        # fetch RPT token
        try:
            self.log.info('Retrieving RPT from keycloak server')
            response = requests.post(
                self.config.token_endpoint,
                data=payload,
                headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to retrieve RPT from keycloak server')
            raise ex

        return response.json()

    def validate_rpt(self, rpt):
        """
        Method to introspect and validate the request party token (RPT)

        Args:
            rpt (str): RPT received

        Raises:
            HTTPError
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
        try:
            self.log.info('Introspecting RPT token')
            response = requests.post(
                self.config.introspection_endpoint,
                data=payload,
                headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to validate RPT from keycloak server')
            raise ex

        return response.json()
