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
        """
        method to retrieve userinfo from the keycloak server

        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.userinfo()
        {'sub': 'e1fbd7d6-ad2b-407f-89cf-6c2b004d78bb', 'email_verified': False, 'preferred_username': 'service-account-python-client', 'email': 'service-account-python-client@placeholder.org'}

        Args:
            access_token (str): access token of the client or user

        Returns:
            dict
        """

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
