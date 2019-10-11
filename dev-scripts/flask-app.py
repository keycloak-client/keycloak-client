#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, session, Response
from keycloak import KeycloakClient
from keycloak.extensions.flask import Authentication


app = Flask(__name__)
app.config["SECRET_KEY"] = "b93eff4ef371491f8dba34af3db2275a"


kc = KeycloakClient()
Authentication(app, kc)


@app.route("/", methods=["GET"])
def home():
    return "Howdy!"


@app.route("/tokens", methods=["GET"])
def tokens():
    _tokens = session["tokens"]
    return Response(_tokens)


@app.route("/userinfo", methods=["GET"])
def userinfo():
    _user = session["user"]
    return Response(_user)


if __name__ == "__main__":
    app.run(debug=True)
