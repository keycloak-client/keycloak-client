# -*- coding: utf-8 -*-
import json
from typing import Any

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from keycloak import AsyncClient


class EndpointHandler(HTTPEndpoint):
    def __init__(self, *args: Any, **kwargs: Any):
        self.kc = kwargs.pop("kc")
        self.redirect_uri = kwargs.pop("redirect_uri")
        super().__init__(*args, **kwargs)


class Login(EndpointHandler):
    async def get(self, request: Request) -> Response:
        url, state = await self.kc.login()
        request.session["state"] = state
        return RedirectResponse(url)


class Logout(EndpointHandler):
    async def get(self, request: Request) -> Response:
        # retrieve tokens
        _tokens = request.session["tokens"]
        tokens = json.loads(_tokens)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # logout from keycloak
        await self.kc.logout(access_token, refresh_token)
        del request.session["tokens"]

        # delete user info
        if "user" in request.session:
            del request.session["user"]

        return RedirectResponse(self.redirect_uri)


class Callback(EndpointHandler):
    async def get(self, request: Request) -> Response:

        # validate state
        state = request.query_params["state"]
        _state = request.session.pop("state", "unknown")
        if state != _state:
            return PlainTextResponse("Invalid state", status_code=403)

        # retrieve tokens
        code = request.query_params["code"]
        tokens = await self.kc.callback(code)

        # starlette sessions do not have the capacity to store the entire tokens
        # so storing only access token and refresh token
        _tokens = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }
        request.session["tokens"] = json.dumps(_tokens)

        # retrieve user info
        access_token = tokens["access_token"]
        user = await self.kc.fetch_userinfo(access_token)
        request.session["user"] = json.dumps(user)

        return RedirectResponse(self.redirect_uri)


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        callback_url: str = "https://localhost:8000/kc/callback",
        login_redirect_uri: str = "/",
        logout_uri: str = "/kc/logout",
        logout_redirect_uri: str = "/",
    ) -> None:
        self.app = app
        self.callback_url = callback_url
        self.login_redirect_uri = login_redirect_uri
        self.logout_uri = logout_uri
        self.logout_redirect_uri = logout_redirect_uri
        self.kc = AsyncClient(callback_url)

    @staticmethod
    def get_url(request: Request) -> str:
        return f"{request.url.scheme}://{request.url.netloc}{request.url.path}"

    @staticmethod
    def is_http(scope: Any) -> bool:
        return scope["type"] == "http"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # handle http requests
        if self.is_http(scope):
            request = Request(scope, receive)

            # handle callback request
            if self.get_url(request) == self.callback_url:
                await Callback(
                    scope,
                    receive,
                    send,
                    kc=self.kc,
                    redirect_uri=self.login_redirect_uri,
                )
                return

            # handle logout request
            elif request.url.path == self.logout_uri:
                await Logout(
                    scope,
                    receive,
                    send,
                    kc=self.kc,
                    redirect_uri=self.logout_redirect_uri,
                )
                return

            # handle logout redirect uri
            elif request.url.path == self.logout_redirect_uri:
                await self.app(scope, receive, send)
                return

            # handle unauthorized requests
            elif "user" not in request.session:
                await Login(
                    scope,
                    receive,
                    send,
                    kc=self.kc,
                    redirect_uri=self.logout_redirect_uri,
                )
                return

            # handle authorized requests
            else:
                await self.app(scope, receive, send)
                return

        # handle non http requests
        await self.app(scope, receive, send)
