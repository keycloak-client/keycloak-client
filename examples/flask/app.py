# -*- coding: utf-8 -*-
from flask import Flask, session, Response
from keycloak.extensions.flask import Authentication


api = Flask(__name__)
api.config["SECRET_KEY"] = "EYxuFcNqGamVU78GgfupoO5N4z2xokA58XtL0ag"


Authentication(api)


@api.route("/")
def home():
    return Response("Welcome Home")


if __name__ == "__main__":
    api.run(host="0.0.0.0", debug=True)
