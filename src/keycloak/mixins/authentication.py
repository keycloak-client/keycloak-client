# -*- coding: utf-8 -*-
import logging
from typing import Tuple, Dict
from urllib.parse import urlencode
from uuid import uuid4

import requests

from ..config import config
from ..constants import GrantTypes, Logger, ResponseTypes
from ..utils import auth_header, handle_exceptions


log = logging.getLogger(Logger.name)


class AuthenticationMixin:
    """
    This class includes the methods to interact with the authentication flow
    """

    _userinfo: Dict = {}
    callback_uri = "http://localhost/kc/callback"

    def login(self, scopes: Tuple = ("openid",)) -> Tuple:
        """
        methot to generate openid login url and state

        >>> from keycloak import Client
        >>> from flask import Flask, request, session, redirect
        >>>
        >>> kc = Client()
        >>>
        >>> app = Flask(__name__)
        >>>
        >>> @app.route("/howdy)
        >>> def howdy():
        >>>     return "Howdy!"
        >>>
        >>> @app.route("/login)
        >>> def login():
        >>>     url, state = kc.login()
        >>>     session["state"] = state
        >>>     return redirect(url)
        >>>
        >>> if __name__ == "__main__":
        >>>     app.run()

        Args:
            scopes (tuple): scopes to be requested eg: openid, email, profile etc

        Returns:
            tuple
        """
        state = uuid4().hex
        arguments = urlencode(
            {
                "state": state,
                "client_id": config.client.client_id,
                "response_type": ResponseTypes.code,
                "scope": " ".join(scopes),
                "redirect_uri": self.callback_uri,
            }
        )
        return f"{config.openid.authorization_endpoint}?{arguments}", state

    @handle_exceptions
    def callback(self, code: str) -> Dict:
        """
        openid login callback handler

        >>> from keycloak import Client
        >>> from flask import Flask, request, session, redirect, Response
        >>>
        >>> kc = Client()
        >>>
        >>> app = Flask(__name__)
        >>>
        >>> @app.route("/howdy)
        >>> def howdy():
        >>>     return "Howdy!"
        >>>
        >>> @app.route("/login)
        >>> def login():
        >>>     url, state = kc.login()
        >>>     session["state"] = state
        >>>     return redirect(url)
        >>>
        >>> @app.route("/callback)
        >>> def callback():
        >>>     state = request.params["state"]
        >>>     if session["state"] != state:
        >>>         return Response("Invalid state", status=400)
        >>>
        >>>     code = request.params["code"]
        >>>     session["tokens"] = kc.callback(code)
        >>>     return redirect("/howdy")
        >>>
        >>> if __name__ == "__main__":
        >>>     app.run()

        Args:
            code (str): code send by the keycloak server

        Returns:
            dict
        """
        payload = {
            "code": code,
            "grant_type": GrantTypes.authorization_code,
            "redirect_uri": self.callback_uri,
            "client_id": config.client.client_id,
            "client_secret": config.client.client_secret,
        }
        log.debug("Retrieving user tokens from server")
        response = requests.post(config.openid.token_endpoint, data=payload)
        response.raise_for_status()
        log.debug("User tokens retrieved successfully")
        return response.json()

    @handle_exceptions
    def fetch_userinfo(self, access_token: str = None) -> Dict:
        """
        method to retrieve userinfo from the keycloak server

        >>>
        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.fetch_userinfo()
        2020-03-14 16:56:41,645 [DEBUG] Loading client config from the settings file
        2020-03-14 16:56:41,645 [DEBUG] Lookup settings file in the env vars
        2020-03-14 16:56:41,647 [DEBUG] Retrieving PAT from server
        2020-03-14 16:56:41,647 [DEBUG] Loading uma2 config using well-known endpoint
        2020-03-14 16:56:41,692 [DEBUG] Retrieving user info from server
        2020-03-14 16:56:41,692 [DEBUG] Loading openid config using well-known endpoint
        2020-03-14 16:56:41,710 [DEBUG] User info retrieved successfully
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        Args:
            access_token (str): access token of the client or user

        Returns:
            dict
        """
        access_token = access_token or self.access_token  # type: ignore
        headers = auth_header(access_token)
        log.debug("Retrieving user info from server")
        response = requests.post(config.openid.userinfo_endpoint, headers=headers)
        response.raise_for_status()
        log.debug("User info retrieved successfully")
        return response.json()

    @property
    def userinfo(self) -> Dict:
        """
        user information available within the server

        >>>
        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.userinfo
        2020-03-14 16:51:24,115 [DEBUG] Loading client config from the settings file
        2020-03-14 16:51:24,115 [DEBUG] Lookup settings file in the env vars
        2020-03-14 16:51:24,118 [DEBUG] Retrieving PAT from server
        2020-03-14 16:51:24,118 [DEBUG] Loading uma2 config using well-known endpoint
        2020-03-14 16:51:24,164 [DEBUG] Retrieving user info from server
        2020-03-14 16:51:24,164 [DEBUG] Loading openid config using well-known endpoint
        2020-03-14 16:51:24,193 [DEBUG] User info retrieved successfully
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        Returns:
            dict
        """
        if not self._userinfo:
            self._userinfo = self.fetch_userinfo()
        return self._userinfo
