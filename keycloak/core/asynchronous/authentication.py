# -*- coding: utf-8 -*-
import logging
from typing import Dict, Tuple
from urllib.parse import urlencode
from uuid import uuid4

import httpx

from keycloak.config import config
from keycloak.constants import GrantTypes, Logger, ResponseTypes
from keycloak.utils import auth_header, handle_exceptions

log = logging.getLogger(Logger.name)


class AsyncAuthenticationMixin:
    """
    This class includes the methods to interact with the authentication flow
    """

    _userinfo: Dict = {}
    callback_uri = "http://localhost/kc/callback"

    async def login(self, scopes: Tuple = ("openid",)) -> Tuple:
        """
        method to generate openid login url and state

        >>> import uvicorn
        >>> from starlette.routing import Route
        >>> from starlette.applications import Starlette
        >>> from starlette.responses import RedirectResponse
        >>> from starlette.middleware import Middleware
        >>> from starlette.middleware.sessions import SessionMiddleware
        >>> from keycloak import AsyncClient
        >>>
        >>> kc= AsyncClient()
        >>>
        >>> async def howdy(request):
        >>>     return "Howdy!"
        >>>
        >>> async def login(request):
        >>>     url, state = await kc.login()
        >>>     request.session["state"] = state
        >>>     return RedirectResponse(url)
        >>>
        >>> routes = [
        >>>     Route("/howdy", howdy),
        >>>     Route("/login", login),
        >>> ]
        >>>
        >>> middlewares = [
        >>>     Middleware(SessionMiddleware, secret_key="bba085e8e95cd42cb19e268f")
        >>> ]
        >>>
        >>> app = Starlette(routes=routes, middleware=middlewares)
        >>>
        >>> if __name__ == "__main__":
        >>>     uvicorn.run(app)

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
    async def callback(self, code: str) -> Dict:
        """
        openid login callback handler

        >>> import uvicorn
        >>> from starlette.routing import Route
        >>> from starlette.applications import Starlette
        >>> from starlette.responses import RedirectResponse, PlainTextResponse
        >>> from starlette.middleware import Middleware
        >>> from starlette.middleware.sessions import SessionMiddleware
        >>> from keycloak import AsyncClient
        >>>
        >>> kc= AsyncClient()
        >>>
        >>> async def howdy(request):
        >>>     return "Howdy!"
        >>>
        >>> async def login(request):
        >>>     url, state = await kc.login()
        >>>     request.session["state"] = state
        >>>     return RedirectResponse(url)
        >>>
        >>> async def callback(request):
        >>>     state = request.query_params["state"]
        >>>     if request.session["state"] != state:
        >>>         return PlainTextResponse("Invalid state", status=400)
        >>>     code = request.query_params["code"]
        >>>     request.session["tokens"] = await kc.callback(code)
        >>>     return RedirectResponse("/howdy")
        >>>
        >>> routes = [
        >>>     Route("/howdy", howdy),
        >>>     Route("/login", login),
        >>>     Route("/callback", callback),
        >>> ]
        >>>
        >>> middlewares = [
        >>>     Middleware(SessionMiddleware, secret_key="bba085e8e95cd42cb19e268f")
        >>> ]
        >>>
        >>> app = Starlette(routes=routes, middleware=middlewares)
        >>>
        >>> if __name__ == "__main__":
        >>>     uvicorn.run(app)

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
        async with httpx.AsyncClient() as client:
            response = await client.post(config.openid.token_endpoint, data=payload)
            log.debug("User tokens retrieved successfully")
            return response.json()

    @handle_exceptions
    async def fetch_userinfo(self, access_token: str = None) -> Dict:
        """
        method to retrieve userinfo from the keycloak server

        >>> import asyncio
        >>> from keycloak import AsyncClient
        >>> kc= AsyncClient()
        >>> asyncio.run(kc.fetch_userinfo())
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        :param access_token: access token of the client or user
        :returns: dicttionary
        """
        access_token = access_token or await self.access_token  # type: ignore
        headers = auth_header(access_token)
        log.debug("Retrieving user info from server")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.openid.userinfo_endpoint, headers=headers
            )
            log.debug("User info retrieved successfully")
            return response.json()

    @property
    async def userinfo(self) -> Dict:
        """
        user information available within the server

        >>> import asyncio
        >>> from keycloak import AsyncClient
        >>> kc = AsyncClient()
        >>> asyncio.run(kc.userinfo)
        {'sub': '4c9c2430-b2e7-4f0b-9325-aa81dffe0463', 'email_verified': False, 'preferred_username': 'service-account-keycloak-client'}
        >>>

        :returns: dictionary
        """
        if not self._userinfo:
            self._userinfo = await self.fetch_userinfo()
        return self._userinfo

    async def logout(self, access_token: str = None, refresh_token: str = None) -> None:
        access_token = access_token or await self.access_token  # type: ignore
        refresh_token = refresh_token or await self.refresh_token  # type: ignore
        payload = {
            "client_id": config.client.client_id,
            "client_secret": config.client.client_secret,
            "refresh_token": refresh_token,
        }
        headers = auth_header(access_token)
        log.debug("Logging out user from server")
        async with httpx.AsyncClient() as client:
            await client.post(
                config.openid.end_session_endpoint, data=payload, headers=headers
            )
            log.debug("User logged out successfully")
