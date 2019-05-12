#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with policies """

import requests


class PolicyMixin:
    """
    This class includes methods to interact with the policy api
    For details see keycloak documentation availabe in the below url
    https://www.keycloak.org/docs/latest/authorization_services/index.html
    """

    def list_policy(self, resource_id):
        """
        Method to list all policy's associated with the client

        Args:
            resource_id (str): id of the resource

        Returns:
            dict

        Raises:
            HTTPError
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + "?resource=" + resource_id

        # fetch list of policies
        try:
            self.log.info("Listing policies associated with resource=%s", resource_id)
            response = requests.get(endpoint, headers=self.pat_auth_header)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception("Failed to list of policies")
            raise ex
        return response.json()

    # pylint: disable=dangerous-default-value
    def create_policy(self, resource_id, policy={}):
        """
        Method to create policy

        Args:
            resource_id (str): resource id
            permisssion (dict): policy to be created

        Example Policy:
        {
            "name": "Student: Read for all",
            "description": "Allow all to read",
            "scopes": [
                "student:read"
            ],
            "roles": [
                "flask-app/AppUser"
            ]
        }
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + "/" + resource_id

        # prepare payload
        policy.update({"clients": [self.config.client_id]})

        # fetch list of policies
        try:
            self.log.info("Creating policy for resource=%s", resource_id)
            response = requests.post(
                endpoint, json=policy, headers=self.pat_auth_header
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception("Failed to create policy")
            print(response.content)
            raise ex

        return response.json()

    # pylint: disable=dangerous-default-value
    def update_policy(self, policy_id, policy={}):
        """
        Method to update the policy

        Args:
            policy_id (str): unique identifier for the policy
            policy (dict): new policy definition
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + "/" + policy_id

        # update policy
        try:
            self.log.info("Updating policy id=%s", policy_id)
            response = requests.put(endpoint, json=policy, headers=self.pat_auth_header)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception("Failed to update policy")
            raise ex

    def delete_policy(self, policy_id):
        """
        Method to delete the policy

        Args:
            policy_id (str): unique identifier for the policy
        """
        # prepare endpoint
        endpoint = self.config.policy_endpoint + "/" + policy_id

        # delete policy
        try:
            self.log.info("Deleting policy id=%s", policy_id)
            response = requests.delete(endpoint, headers=self.pat_auth_header)
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            self.log.exception("Failed to delete policy")
            raise ex
