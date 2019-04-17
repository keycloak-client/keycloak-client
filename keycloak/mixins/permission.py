#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with policies """

import requests


class PermissionMixin:
    """
    This class includes methods to interact with the permission api
    For details see keycloak documentation availabe in the below url
    https://www.keycloak.org/docs/latest/authorization_services/index.html#_service_authorization_uma_policy_api
    """

    def list_permission(self, aat=None):
        """
        Method to list all permissions associated with the user/client

        Args:
            aat (str): access token

        Returns:
            dict

        Raises:
            InvalidAAT
            HTTPError
        """
        # prepare headers
        headers = {
            'Authorization': 'Bearer %s' % aat
        }

        # fetch list of policies
        try:
            self.log.info('Fetching list of permissions')
            response = requests.get(self.config.policy_endpoint, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to fetch the list of permissions')
            raise ex
        return response.json()

    # pylint: disable=dangerous-default-value
    def create_permission(self, aat=None, resource_id=None, permission={}):
        """
        Method to create permission

        Args:
            aat (str): access token
            resource_id (str): resource id
            permisssion (dict): permission to be created
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + '/' + resource_id

        # prepare headers
        headers = {
            'Authorization': 'Bearer %s' % aat
        }

        # prepare payload
        permission.update({
            'clients': [self.config.client_id]
        })

        # fetch list of policies
        try:
            self.log.info('Creating permission for resource id=%s', resource_id)
            response = requests.post(endpoint, json=permission, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to fetch the list of permissions')
            raise ex

        return response.json()

    # pylint: disable=dangerous-default-value
    def update_permission(self, aat=None, permission_id=None, permission={}):
        """
        Method to update the permission

        Args:
            aat (str): access token
            permission_id (str): unique identifier for the permission
            permission (dict): new permission definition
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + '/' + permission_id

        # prepare headers
        headers = {
            'Authorization': 'Bearer %s' % aat
        }

        # update permission
        try:
            self.log.info('Updating permission id=%s', permission_id)
            response = requests.put(endpoint, json=permission, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to update permission')
            raise ex

    def delete_permission(self, aat=None, permission_id=None):
        """
        Method to delete the permission

        Args:
            aat (str): acccess token
            permission_id (str): unique identifier for the permission
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + '/' + permission_id

        # prepare headers
        headers = {
            'Authorization': 'Bearer %s' % aat
        }

        # delete permission
        try:
            self.log.info('Deleting permission id=%s', permission_id)
            response = requests.delete(endpoint, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception('Failed to delete permission')
            raise ex
