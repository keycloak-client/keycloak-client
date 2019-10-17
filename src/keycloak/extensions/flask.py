# -*- coding: utf-8 -*-
import json
from typing import Union

from flask import Flask, redirect, request, session
from werkzeug.wrappers import Response

from .. import Client


class Authentication:
    def __init__(self, app: Flask, redirect_uri: str) -> None:
        """ Initialize extension """
        self.app = app
        self.kc = Client(redirect_uri=redirect_uri)
        self.add_routes(app)

    def add_routes(self, app: Flask) -> None:
        """ add middleware and routes """
        app.add_url_rule("/kc/login", "kc-login", self.login)
        app.add_url_rule("/kc/callback", "kc-callback", self.callback)
        app.before_request(self.is_logged_in)

    @staticmethod
    def is_logged_in() -> Union[None, Response]:
        """ Middleware to verify whether the user has logged in or not """
        if any(["tokens" not in session, "user" not in session]) and (
            "/kc" not in request.path
        ):
            return redirect("/kc/login")
        else:
            return None

    def login(self) -> Response:
        """ Initiate authentication """
        url, state = self.kc.login()
        session["state"] = state
        return redirect(url)

    def callback(self) -> Response:
        """ Authentication callback handler """

        # validate state
        state = request.args.get("state", "unknown")
        _state = session.pop("state", None)
        if state != _state:
            return Response("Invalid state", status=403)

        # fetch user tokens
        code: str = request.args.get("code", "unknown")
        tokens = self.kc.callback(code)
        session["tokens"] = json.dumps(tokens)

        # fetch user info
        access_token = tokens["access_token"]
        user = self.kc.userinfo(access_token)
        session["user"] = json.dumps(user)

        return redirect("/")


class Authorization:
    pass
