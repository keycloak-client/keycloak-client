#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with resources """

import requests
from cached_property import cached_property, cached_property_with_ttl


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
        payload = {
            'grant_type': 'client_credentials'
        }

        # prepare headers
        headers = {
            'Authorization': self.basic_authorization_header
        }

        # retrieve PAT
        response = requests.post(self.config.token_endpoint, data=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    @cached_property
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

        # list resource
        self.log.info('Fetching list of resources')
        response = requests.get(self.config.resource_registration_endpoint, headers=self.headers)
        response.raise_for_status()

        return response.json()

    # pylint: disable=dangerous-default-value
    def create_resource(self, resource={}):
        """
        Method to create resource

        Args:
            resource (dict): resources to be created

        example:
        {
            "name": "student",
            "uris": ["/student/*"],
            "scopes": ["create", "read", "update", "delete"]
          }
        """
        response = requests.post(
            self.config.resource_registration_endpoint,
            json=resource,
            headers=self.headers
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
        endpoint = self.config.resource_registration_endpoint + resource_id

        # create resource
        response = requests.get(endpoint, headers=self.headers)
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
        endpoint = self.config.resource_registration_endpoint + resource_id

        # update resource
        response = requests.put(endpoint, json=resource, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def delete_resource(self, resource_id):
        """
        Method to delete resource

        Args:
            resource_id (str): id of the resource to be deleted
        """

        # prepare endpoint
        endpoint = self.config.resource_registration_endpoint + resource_id

        # create resource
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def register_resources(self, resources_file=None):
        """
        Method to register resources in the keycloak server

        Args:
            resources_file (str): file path

        Example:
        [
          {
            "resource":{
              "name":"student",
              "type":"urn:flask-app:resources:student",
              "uris":[
                "/student/*"
              ],
              "scopes":[
                "student:create",
                "student:read",
                "student:update",
                "student:delete"
              ],
              "ownerManagedAccess":"true"
            },
            "permissions":[
              {
                "name":"Student: Read for all",
                "description":"Allow all app users to read",
                "scopes":[
                  "student:read"
                ],
                "roles":[
                  "AppUser"
                ]
              },
              {
                "name":"Student: Delete for admins",
                "description":"Allow admin users to delete",
                "scopes":[
                  "student:delete"
                ],
                "roles":[
                  "Administrator"
                ]
              }
            ]
          }
        ]
        """
        # read resouces file
        with open(resources_file) as f:
            records = json.loads(f.read())

        # iterate over resources
        for record in records:

            # parse resource and permissions
            resource = record.get('resource')
            permissions = record.get('permissions')

            # create resource
            self.log.info('Processing resource %s', resource['name'])
            resource = self.create_resource(resource)

            # create policies
            for permission in permissions:
                self.log.info('Processing permission %s', permission['name'])
                self.create_permission(self.pat['access_token'], resource['_id'], permission)
