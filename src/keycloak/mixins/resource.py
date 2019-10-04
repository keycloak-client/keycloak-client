# -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with resources """

import requests
from cached_property import cached_property_with_ttl

from ..constants import TokenType
from ..utils import auth_header


class ResourceMixin:
    """
    This class includes methods to interact with the protection api
    For details see keycloak documentation availabe in the below url
    https://www.keycloak.org/docs/5.0/authorization_services/#_service_protection_api
    """

    @cached_property_with_ttl(ttl=300)
    def pat(self):
        """
        Protection API Token (PAT)

        Returns:
             dict
        """
        # prepare payload
        payload = {"grant_type": "client_credentials"}

        # retrieve PAT
        response = requests.post(
            self.config.token_endpoint, data=payload, headers=self.basic_auth_header
        )
        response.raise_for_status()

        return response.json()

    @property
    def pat_auth_header(self):
        """ Common headers used within the class """
        return auth_header(self.pat["access_token"], TokenType.BEARER)

    def list_resource(self):
        """
        Method to list all resources associated with the client

        Returns:
            dict
        """

        # list resource
        self.log.info("Fetching list of resources")
        response = requests.get(
            self.config.resource_registration_endpoint, headers=self.pat_auth_header
        )
        response.raise_for_status()

        return response.json()

    def create_resource(self, resource={}):
        """
        Method to create resource

        Args:
            resource (dict): resources to be created

        example:
          {
            "name": "student",
            "type": "urn:flask-app:resources:student",
            "uris": ["/student/*"],
            "scopes": ["create", "read", "update", "delete"]
          }
        """
        response = requests.post(
            self.config.resource_registration_endpoint,
            json=resource,
            headers=self.pat_auth_header,
        )
        response.raise_for_status()
        return response.json()

    def read_resource(self, resource_id):
        """
        Method to read resource

        Args:
            resource_id (str): id of the resource to be read
        """

        # prepare endpoint
        endpoint = f"{self.config.resource_registration_endpoint}/{resource_id}"

        # create resource
        response = requests.get(endpoint, headers=self.pat_auth_header)
        response.raise_for_status()

        return response.json()

    def update_resource(self, resource_id, resource):
        """
        Method to update resource

        Args:
            resource_id (str): id of the resource to be updated
            resource (dict): resource to be updated
        """

        # prepare endpoint
        endpoint = f"{self.config.resource_registration_endpoint}/{resource_id}"

        # update resource
        response = requests.put(endpoint, json=resource, headers=self.pat_auth_header)
        response.raise_for_status()

        return response.json()

    def delete_resource(self, resource_id):
        """
        Method to delete resource

        Args:
            resource_id (str): id of the resource to be deleted
        """

        # prepare endpoint
        endpoint = f"{self.config.resource_registration_endpoint}/{resource_id}"

        # create resource
        response = requests.delete(endpoint, headers=self.pat_auth_header)
        response.raise_for_status()

        return response.json()
