# -*- coding: utf-8 -*-
import logging
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
        """ method to fetch the list of resources available """

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
