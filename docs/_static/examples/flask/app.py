# -*- coding: utf-8 -*-
import json

from flask import Flask, jsonify, redirect, request

from keycloak import KeycloakClient


app = Flask(__name__)
keycloak_client = KeycloakClient()


@app.route("/login", methods=["GET"])
def login():
    """ Endpoint to initiate authentication """
    auth_url = keycloak_client.authentication_url()
    return redirect(auth_url)


@app.route("/login-callback", methods=["GET"])
def login_callback():
    """ Endpoint to retrieve authentication tokens """
    code = request.args.get("code")
    tokens = keycloak_client.authentication_callback(code)
    return jsonify(tokens)


@app.route("/retrieve-rpt", methods=["POST"])
def retrieve_rpt():
    """ Endpoint to retrieve authorization tokens """
    aat = request.json.get("aat")
    result = keycloak_client.retrieve_rpt(aat)
    return jsonify(result)


@app.route("/introspect-rpt", methods=["POST"])
def introspect_rpt():
    """ Endpoint to introspect/validate authorization tokens """
    rpt = request.json.get("rpt")
    result = keycloak_client.validate_rpt(rpt)
    return jsonify(result)


@app.cli.command()
def create_resources():
    """ command to register resources with keycloak """

    # read resources from json
    with open("resources.json", "r") as f:
        resources = f.read()

    # create resources in the keycloak server
    resources = json.loads(resources)
    for item in resources:
        keycloak_client.create_resource(item)


if __name__ == "__main__":
    app.run(debug=True)
