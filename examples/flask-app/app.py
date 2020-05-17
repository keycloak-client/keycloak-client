# -*- coding: utf-8 -*-
from flask import Flask, session
from keycloak.extensions.flask import AuthenticationMiddleware


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret0123456789"
app.wsgi_app = AuthenticationMiddleware(
    app.wsgi_app,
    app.config,
    app.session_interface,
    callback_url="http://localhost:5000/kc/callback",
    redirect_url="/howdy",
)


@app.route("/howdy")
def howdy():
    user = session["user"]
    return f"Howdy {user}"


if __name__ == "__main__":
    app.run()
