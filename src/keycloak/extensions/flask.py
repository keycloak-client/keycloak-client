# -*- coding: utf-8 -*-
import json

from flask import Flask, Response, redirect, request, session

from .. import Client


class Authentication:
    def __init__(self, app: Flask, kc: Client, redirect_to: str = "/"):
        """ Initialize extension """
        self.app = app
        self.kc = kc
        self.redirect_to = redirect_to
        self.add_routes(app)

    def add_routes(self, app: Flask):
        """ add middleware and routes """
        app.add_url_rule("/kc/login", "kc-login", self.login)
        app.add_url_rule("/kc/callback", "kc-callback", self.callback)
        app.before_request(self.is_logged_in)

    @staticmethod
    def is_logged_in():
        """ Middleware to verify whether the user has logged in or not """
        if any(["tokens" not in session, "user" not in session]) and (
            "/kc" not in request.path
        ):
            return redirect("/kc/login")

    def login(self):
        """ Initiate authentication """
        url, state = self.kc.login()
        session["state"] = state
        return redirect(url)

    def callback(self):
        """ Authentication callback handler """

        # validate state
        state = request.args.get("state", "unknown")
        _state = session.pop("state", None)
        if state != _state:
            return Response("Invalid state", status=403)

        # fetch user tokens
        code = request.args.get("code")
        tokens = self.kc.callback(code)
        session["tokens"] = json.dumps(tokens)

        # fetch user info
        access_token = tokens["access_token"]
        user = self.kc.userinfo(access_token)
        session["user"] = json.dumps(user)

        return redirect(self.redirect_to)


class Authorization:
    pass
