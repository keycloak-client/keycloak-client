# -*- coding: utf-8 -*-

from flask import Response, redirect, request, session

from keycloak import KeycloakClient


class Authentication:
    def __init__(self, app=None):
        self.app = app
        self.keycloak_client = KeycloakClient()
        if app is not None:
            self.add_routes(app)

    def add_routes(self, app):
        """ Initialize extension """
        app.add_url_rule("/keycloak/login", "keycloak-login", self.login)
        app.add_url_rule("/keycloak/callback", "keycloak-callback", self.callback)
        app.before_request(self.is_logged_in)

    @staticmethod
    def is_logged_in():
        """ Middleware  to verify whether the user has logged in or not """
        if all(["user" not in session, "/keycloak" not in request.path]):
            return redirect("/keycloak/login")

    def login(self):
        """ Initiate authentication """
        auth_url, state = self.keycloak_client.authentication_url()
        session["state"] = state
        return redirect(auth_url)

    def callback(self):
        """ Authentication callback handler """
        code = request.args.get("code")
        state = request.args.get("state", "unknown")
        _state = session.pop("state", None)
        if state != _state:
            return Response("Invalid state", status=403)
        response = self.keycloak_client.authentication_callback(code)
        session["user"] = self.keycloak_client.decode_jwt(response["id_token"])
        return redirect("/")
