# -*- coding: utf-8 -*-
import json

from keycloak import Client
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.endpoints import HTTPEndpoint


kc = Client()


class Login(HTTPEndpoint):
    async def get(self, request):
        url, state = kc.login()
        request.session["state"] = state
        return RedirectResponse(url)


class Callback(HTTPEndpoint):
    def __init__(self, *args, **kwargs):
        self.redirect_to = kwargs.pop("redirect_to", "/")
        super().__init__(*args, **kwargs)

    async def get(self, request):
        # validate state
        state = request.query_params["state"]
        _state = request.session.pop("state", "unknown")
        if state != _state:
            return PlainTextResponse("Invalid state", status_code=403)

        # retreive tokens
        code = request.query_params["code"]
        tokens = kc.callback(code)
        # waiting for https://github.com/encode/starlette/pull/499
        # request.session["tokens"] = json.dumps(tokens)

        # retrieve user info
        access_token = tokens["access_token"]
        user = kc.userinfo(access_token)
        request.session["user"] = json.dumps(user)

        return RedirectResponse(self.redirect_to)


class Authentication:
    def __init__(self, app: ASGIApp, redirect_to: str = "/") -> None:
        self.app = app
        self.redirect_to = redirect_to

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)

        if request.url.path == "/kc/callback":
            await Callback(scope, receive, send, redirect_to=self.redirect_to)

        elif any(["/kc/login" in request.url.path, "user" not in request.session]):
            await Login(scope, receive, send)

        else:
            await self.app(scope, receive, send)
