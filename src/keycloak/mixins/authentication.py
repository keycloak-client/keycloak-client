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
        method to generate openid login url and state

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

        :param scopes: scopes to be requested eg: openid, email, profile etc

        :returns: endpoint url and state
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

        :param code: code send by the keycloak server
        :returns: dictionary
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
        >>> kc = Client()
        >>> kc.fetch_userinfo()
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        :param access_token: access token of the client or user
        :returns: dicttionary
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
        >>> kc = Client()
        >>> kc.userinfo
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        :returns: dictionary
        """
        if not self._userinfo:
            self._userinfo = self.fetch_userinfo()
        return self._userinfo

    def logout(self, access_token: str = None, refresh_token: str = None) -> None:
        access_token = access_token or self.access_token  # type: ignore
        refresh_token = refresh_token or self.refresh_token  # type: ignore
        payload = {
            "client_id": config.client.client_id,
            "client_secret": config.client.client_secret,
            "refresh_token": refresh_token,
        }
        headers = auth_header(access_token)
        log.debug("Logging out user from server")
        response = requests.post(
            config.openid.end_session_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("User logged out successfully")
