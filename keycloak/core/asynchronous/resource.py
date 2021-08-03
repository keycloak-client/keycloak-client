# -*- coding: utf-8 -*-
import logging
from typing import Dict, List

import httpx

from keycloak.config import config
from keycloak.constants import Logger
from keycloak.utils import auth_header, handle_exceptions

log = logging.getLogger(Logger.name)


class AsyncResourceMixin:
    """
    This class consists of methods that can be used to manage resources
    """

    _resources: List = []

    @property
    async def resources(self) -> List:
        """
        list of resources available in keycloak server

        >>> import asyncio
        >>> from keycloak import AsyncClient
        >>> kc= AsyncClient()
        >>> asyncio.run(await kc.resources)
        [{'name': 'default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}]
        >>>

        :returns: list
        """
        if not self._resources:
            self._resources = await self.find_resources()
        return self._resources

    @handle_exceptions
    async def find_resources(self, access_token: str = None) -> List:
        """
        fetch resources from keycloak server

        >>> import asyncio
        >>> from keycloak import AsyncClient
        >>> kc= AsyncClient()
        >>> asyncio.run(await kc.find_resources())
        [{'name': 'default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}]
        >>>

        :param access_token: access token to be used
        :returns: list
        """
        access_token = access_token or await self.access_token  # type: ignore
        headers = auth_header(access_token)
        log.debug("Retrieving resources from keycloak")
        async with httpx.AsyncClient() as client:
            response = await client.get(config.uma2.resource_endpoint, headers=headers)
            log.debug("Resources retrieved successfully")
            return [await self.find_resource(x, access_token) for x in response.json()]  # type: ignore

    @handle_exceptions
    async def find_resource(self, resource_id: str, access_token: str = None) -> Dict:
        """
        Method to fetch the details of a resource

        >>> import asyncio
        >>> from keycloak import AsyncClient
        >>> kc= AsyncClient()
        >>> asyncio.run(await kc.find_resource('bb6a777f-a17b-4555-b035-a6ce12a1fd21'))
        {'name': 'default Resource', 'type': 'urn:python-client:resources:default', 'owner': {'id': 'd74cc555-d46c-4ef8-8a30-ceb2b91d8823'}, 'ownerManagedAccess': False, 'attributes': {}, '_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'uris': ['/*'], 'resource_scopes': []}
        >>>

        :param resource_id: id of the resource
        :param access_token: access token to be used
        :returns: list
        """
        access_token = access_token or await self.access_token  # type: ignore
        headers = auth_header(access_token)
        endpoint = f"{config.uma2.resource_endpoint}/{resource_id}"
        log.debug("Retrieving resource from keycloak")
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=headers)
            log.debug("Resource retrieved successfully")
            return response.json()
