# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from typing import List, Dict

import requests

from ..config import config
from ..constants import Logger
from ..utils import auth_header, handle_exceptions


log = logging.getLogger(Logger.name)


class ResourceMixin:
    """
    This class consists of methods that can be used to manage resources
    """

    _resources: List = []

    @property
    def resources(self) -> List:
        """
        list of resources available in keycloak server

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.resources
        [{'name': 'Default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}]
        >>>

        :returns: list
        """
        if not self._resources:
            self._resources = self.find_resources()
        return self._resources

    @handle_exceptions
    def find_resources(self, access_token: str = None) -> Dict:
        """
        fetch resources from keycloak server

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.find_resources()
        [{'name': 'Default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}]
        >>>

        :param access_token: access token to be used
        :returns: list
        """
        access_token = access_token or self.access_token  # type: ignore
        headers = auth_header(access_token)
        log.debug("Retrieving resources from keycloak")
        response = requests.get(config.uma2.resource_endpoint, headers=headers)
        response.raise_for_status()
        log.debug("Resources retrieved successfully")
        return [self.find_resource(x) for x in response.json()]  # type: ignore

    @handle_exceptions
    def find_resource(self, resource_id: str, access_token: str = None) -> Dict:
        """
        Method to fetch the details of a resource

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.find_resource('bb6a777f-a17b-4555-b035-a6ce12a1fd21')
        {'name': 'Default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}
        >>>

        :param access_token: access token to be used
        :returns: list
        """
        access_token = access_token or self.access_token  # type: ignore
        headers = auth_header(access_token)
        endpoint = f"{config.uma2.resource_endpoint}/{resource_id}"
        log.debug("Retrieving resource from keycloak")
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        log.debug("Resource retrieved successfully")
        return response.json()
