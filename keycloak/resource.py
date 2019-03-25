#! -*- coding: utf-8 -*-
import requests


class ResourceMixin(object):
    """
    This class includes methods to interact with the protection api
    For details see https://www.keycloak.org/docs/5.0/authorization_services/#_service_protection_api
    """

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

    @property
    def headers(self):
        """ Common headers used within the class """
        return {
            'Authorization': 'Bearer {}'.format(self.pat['access_token'])
        }

    def list_resource(self):
        """
        Method to list all resources associated with the client

        Returns:
            dict
        """

        # create resource
        response = requests.get(self.config['resource_endpoint'], headers=self.headers)
        response.raise_for_status()

        return response.json()

    def create_resource(self, name, uris=[], scopes=[]):
        """
        Method to create resource

        Args:
            name (str): name of the resource
            uris (list): set of uris protected by the resource
            scopes (list): list of scopes
        """

        # prepare payload
        payload = {
            'name': name,
            'uris': uris,
            'scopes': scopes,
        }

        # create resource
        response = requests.post(self.config['resource_endpoint'], json=payload, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def read_resource(self, resource_id):
        """
        Method to read resource

        Args:
            resource_id (str): id of the resource to be read
        """

        # prepare endpoint
        endpoint = self.config['resource_endpoint'] + resource_id

        # create resource
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def update_resource(self, resource_id, name, scopes=[]):
        """
        Method to update resource

        Args:
            resource_id (str): id of the resource to be updated
            name (str): name of the resource
            scopes (list): list of scopes
        """
        # prepare payload
        payload = {
            'name': name,
            'scopes': scopes,
        }

        # prepare endpoint
        endpoint = self.config['resource_endpoint'] + resource_id

        # update resource
        response = requests.get(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def delete_resource(self, resource_id):
        """
        Method to delete resource

        Args:
            resource_id (str): id of the resource to be deleted
        """

        # prepare endpoint
        endpoint = self.config['resource_endpoint'] + resource_id

        # create resource
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()

        return response.json()
