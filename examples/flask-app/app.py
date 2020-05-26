# -*- coding: utf-8 -*-
from flask import Flask, session
from keycloak.extensions.flask import AuthenticationMiddleware


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret0123456789"
app.wsgi_app = AuthenticationMiddleware(
    app.wsgi_app,
    app.config,
    app.session_interface,
    callback_url="http://testserver:5000/kc/callback",
    redirect_uri="/",
    logout_uri="/logout",
)


@app.route("/")
def howdy():
    user = session["user"]
    return f"Howdy {user}"


@app.route("/logout")
def logout():
    return "User logged out successfully"


if __name__ == "__main__":
    app.run()
