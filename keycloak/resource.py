#! -*- coding: utf-8 -*-
import requests


class ResourceMixin(object):
    """ This class includes methods to interact with the protection api token (PAT) """

    @property
    def pat(self):
        """
        Protection API Token (PAT)

        Returns:
             dict
        """
        # prepare payload
        payload = {
            'grant_type': 'client_credentials'
        }

        # prepare headers
        headers = {
            'Authorization': self.basic_authorization_header
        }

        # retrieve PAT
        response = requests.post(self.config['token_endpoint'], data=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    def create_resource(self, name=None, scopes=[]):
        """
        Method to create resource in the keycloak server

        Args:
            name (str): name of the resource
            scopes (list): list of scopes
        """

        # prepare payload
        payload = {
            'name': name,
            'scopes': scopes,
        }

        # prepare headers
        headers = {
            'Authorization': 'Bearer {}'.format(self.pat['access_token'])
        }

        # create resource
        response = requests.post(self.config['resource_endpoint'], json=payload, headers=headers)
        response.raise_for_status()

        return response.json()
