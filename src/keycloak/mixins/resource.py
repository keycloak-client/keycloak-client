# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from typing import List, Dict

import requests

from ..config import config
from ..constants import Logger
from ..utils import auth_header


log = logging.getLogger(Logger.name)


class ResourceMixin:
    """
    This class consists of methods that can be used to manage resources
    """

    def resources(self, access_token: str = None) -> Dict:
        """
        Method to fetch the list of resources available

        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.resources()
        ['bb6a777f-a17b-4555-b035-a6ce12a1fd21']

        Args:
            access_token (str): access token to be used

        Returns:
            list
        """

        # populate access_token
        access_token = (
            access_token if access_token else self.access_token  # type: ignore
        )

        # prepare headers
        headers = auth_header(access_token)

        # retrieve resource
        log.info("Retrieving list of resources from keycloak server")
        response = requests.get(config.uma2.resource_endpoint, headers=headers)
        try:
            response.raise_for_status()
        except Exception as ex:
            log.exception(
                "Failed to retrieve list of resources from keycloak server\n %s",
                response.content,
            )
            raise ex

        return response.json()

    def resource(self, resource_id: str, access_token: str = None) -> Dict:
        """
        Method to fetch the details of a resource

        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.resources()
        ['bb6a777f-a17b-4555-b035-a6ce12a1fd21']
        >>>
        >>> kc.resource('bb6a777f-a17b-4555-b035-a6ce12a1fd21')
        {'name': 'Default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}

        Args:
            access_token (str): access token to be used

        Returns:
            list
        """

        # populate access_token
        access_token = (
            access_token if access_token else self.access_token  # type: ignore
        )

        # prepare headers
        headers = auth_header(access_token)

        # prepare endpoint
        endpoint = f"{config.uma2.resource_endpoint}/{resource_id}"

        # retrieve resource
        log.info("Retrieving resource from keycloak server")
        response = requests.get(endpoint, headers=headers)
        try:
            response.raise_for_status()
        except Exception as ex:
            log.exception(
                "Failed to find the resource in keycloak server\n %s", response.content
            )
            raise ex

        return response.json()
