# -*- coding: utf-8 -*-
import logging
from typing import Tuple, Dict
from urllib.parse import urlencode
from uuid import uuid4

import requests

from ..config import config
from ..constants import GrantTypes, Logger, ResponseTypes
from ..utils import auth_header


log = logging.getLogger(Logger.name)


class AuthenticationMixin:
    """
    This class includes the methods to interact with the authentication flow
    """

    redirect_uri = "http://localhost/kc/callback"

    def login(self, scopes: Tuple = ("openid",)) -> Tuple:
        """ openid login url """
        log.info("Constructing authentication url")
        state = uuid4().hex
        arguments = urlencode(
            {
                "state": state,
                "client_id": config.client.client_id,
                "response_type": ResponseTypes.code,
                "scope": " ".join(scopes),
                "redirect_uri": self.redirect_uri,
            }
        )
        return f"{config.openid.authorization_endpoint}?{arguments}", state

    def callback(self, code: str) -> Dict:
        """ openid login callback handler """

        # prepare request payload
        payload = {
            "code": code,
            "grant_type": GrantTypes.authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": config.client.client_id,
            "client_secret": config.client.client_secret,
        }

        # retrieve tokens from keycloak server
        log.info("Retrieving user tokens from keycloak server")
        response = requests.post(config.openid.token_endpoint, data=payload)
        try:
            response.raise_for_status()
        except Exception as ex:
            log.exception(
                "Failed to retrieve AAT from keycloak server\n %s", response.content
            )
            raise ex

        return response.json()

    def userinfo(self, access_token: str = None) -> Dict:

        # populate access_token
        access_token = (
            access_token if access_token else self.access_token  # type: ignore
        )

        # prepare headers
        headers = auth_header(access_token)

        # retrieve user info
        log.info("Retrieving user info from keycloak server")
        response = requests.post(config.openid.userinfo_endpoint, headers=headers)
        try:
            response.raise_for_status()
        except Exception as ex:
            log.exception(
                "Failed to retrieve user info from keycloak server\n %s",
                response.content,
            )
            raise ex

        return response.json()
