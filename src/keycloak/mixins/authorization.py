# -*- coding: utf-8 -*-
import logging
from typing import Tuple, Dict

import requests

from ..config import config
from ..constants import Logger, TokenType, GrantTypes, TokenTypeHints
from ..utils import auth_header, basic_auth


log = logging.getLogger(Logger.name)


class AuthorizationMixin:
    """
    This class include methods that interact with the authorization api
    For details see https://www.keycloak.org/docs/5.0/authorization_services/index.html
    """

    @staticmethod
    def payload_for_client() -> Dict:
        """ method to generate payload for client """
        return {"grant_type": GrantTypes.client_credentials}

    @staticmethod
    def payload_for_user(username: str = None, password: str = None) -> Dict:
        """ method to generate payload for user """
        if username and password:
            return {
                "grant_type": GrantTypes.password,
                "username": username,
                "password": password,
            }
        else:
            return {}

    @staticmethod
    def pat(username: str = None, password: str = None) -> Dict:
        """ method to retrieve protection api token (PAT) """

        # prepare headers
        headers = basic_auth(config.client.client_id, config.client.client_secret)

        # prepare payload
        payload = (
            AuthorizationMixin.payload_for_user(username, password)
            or AuthorizationMixin.payload_for_client()
        )

        # retrieve PAT
        log.info("Retrieving protection api token from keycloak server")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception(
                "Failed to retrieve protection api token from keycloak server\n %s",
                response.content,
            )
            raise ex

        return response.json()

    def ticket(self, resources: Tuple, access_token: str = None) -> Dict:
        """ method to retrieve permission ticket """

        # populate access_token
        access_token = (
            access_token if access_token else self.access_token  # type: ignore
        )

        # prepare headers
        headers = auth_header(access_token, TokenType.bearer)

        # retrieve permission ticket
        log.info("Retrieving permission ticket from keycloak server")
        response = requests.post(
            config.uma2.permission_endpoint, json=resources, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception(
                "Failed to retrieve the permission ticket\n %s", response.content
            )
            raise ex

        return response.json()

    def rpt(self, ticket: str, access_token: str = None) -> Dict:
        """ method to fetch the request party token """

        # populate access_token
        access_token = (
            access_token if access_token else self.access_token  # type: ignore
        )

        # prepare payload
        payload = {"grant_type": GrantTypes.uma_ticket, "ticket": ticket}

        # prepare headers
        headers = auth_header(access_token, TokenType.bearer)

        # fetch RPT token
        log.info("Retrieving RPT from keycloak server")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception(
                "Failed to retrieve RPT from keycloak server\n %s", response.content
            )
            raise ex

        return response.json()

    @staticmethod
    def introspect(rpt: str) -> Dict:
        """ method to introspect the request party token """

        # prepare payload
        payload = {"token_type_hint": TokenTypeHints.rpt, "token": rpt}

        # prepare headers
        headers = basic_auth(config.client.client_id, config.client.client_secret)

        # introspect token
        log.info("Introspecting RPT token")
        response = requests.post(
            config.uma2.introspection_endpoint, data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception(
                "Failed to validate RPT from keycloak server\n %s", response.content
            )
            raise ex

        return response.json()
