#! -*- coding: utf-8 -*-
from flask import Flask, request, redirect, jsonify, Response
from keycloak import KeycloakClient


# create keycloak client
keycloak_client = KeycloakClient()


# create flask app
app = Flask(__name__)


@app.route('/login', methods=['GET'])
def login():
    """ Endpoint to initiate authentication """
    return redirect(keycloak_client.authentication_url)


@app.route('/login-callback', methods=['GET'])
def login_callback():
    """ Endpoint to retrieve authentication tokens """
    code = request.args.get('code')
    tokens = keycloak_client.authentication_callback(code)
    return jsonify(tokens)


@app.route('/retrieve-rpt', methods=['POST'])
def retrieve_rpt():
    """ Endpoint to retrieve authorization tokens """
    rpt = request.json.get('rpt')
    result = keycloak_client.retrieve_rpt(rpt)
    return jsonify(result)


@app.route('/introspect-rpt', methods=['POST'])
def introspect_rpt():
    """ Endpoint to introspect/validate authorization tokens """
    rpt = request.json.get('rpt')
    result = keycloak_client.validate_rpt(rpt)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
