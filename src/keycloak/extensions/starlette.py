# -*- coding: utf-8 -*-
import json
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, PlainTextResponse
from starlette.endpoints import HTTPEndpoint

from .. import Client


class EndpointHandler(HTTPEndpoint):
    def __init__(self, *args: Any, **kwargs: Any):
        self.kc = kwargs.pop("kc")
        self.redirect_uri = kwargs.pop("redirect_uri", "/")
        super().__init__(*args, **kwargs)


class Login(EndpointHandler):
    async def get(self, request: Request) -> Response:
        url, state = self.kc.login()
        request.session["state"] = state
        return RedirectResponse(url)


class Callback(EndpointHandler):
    async def get(self, request: Request) -> Response:
        # validate state
        state = request.query_params["state"]
        _state = request.session.pop("state", "unknown")
        if state != _state:
            return PlainTextResponse("Invalid state", status_code=403)

        # retrieve tokens
        code = request.query_params["code"]
        tokens = self.kc.callback(code)

        # retrieve user info
        access_token = tokens["access_token"]
        user = self.kc.fetch_userinfo(access_token)
        request.session["user"] = json.dumps(user)

        return RedirectResponse(self.redirect_uri)


class AuthenticationMiddleware:
    def __init__(
        self, app: ASGIApp, callback_uri: str, redirect_uri: str = "/"
    ) -> None:
        self.app = app
        self.callback_uri = callback_uri
        self.redirect_uri = redirect_uri
        self.kc = Client(callback_uri)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # handle http requests
        if (scope["type"] == "http") and (scope["scheme"] == "http"):
            request = Request(scope, receive)

            # handle callback request
            if request.url.path == "/kc/callback":
                await Callback(scope, receive, send, kc=self.kc)

            # handle unauthorized requests
            elif ("/kc/callback" not in request.url.path) and (
                "user" not in request.session
            ):
                await Login(scope, receive, send, kc=self.kc)

            # handle authorized requests
            else:
                await self.app(scope, receive, send)

        # handle non http requests
        else:
            await self.app(scope, receive, send)
