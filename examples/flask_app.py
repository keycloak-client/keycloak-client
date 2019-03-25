#! -*- coding: utf-8 -*-
from flask import Flask, request, redirect, jsonify, Response
from keycloak import KeycloakClient


# create keycloak client
keycloak_client = KeycloakClient()


# create flask app
app = Flask(__name__)


@app.route('/login', methods=['GET'])
def login():
    """ Endpoint to initiate login """
    return redirect(keycloak_client.authentication_url)


@app.route('/login-callback', methods=['GET'])
def callback():
    """ Endpoint to retrieve user tokens """
    code = request.args.get('code')
    tokens = keycloak_client.authentication_callback(code)
    return jsonify(tokens)


@app.route('/retrieve-rpt', methods=['POST'])
def rpt():
    """ Endpoint to fetch RPT """

    # validate input
    access_token = request.json.get('access_token')
    if access_token is None:
        return Response('access_token missing', status=400)

    # fetch RPT
    result = keycloak_client.retrieve_rpt(access_token)
    return jsonify(result)


@app.route('/introspect-rpt', methods=['POST'])
def introspect_rpt():
    """ Endpoint to introspect RPT """

    # validate input
    access_token = request.json.get('access_token')
    if access_token is None:
        return Response('access_token missing', status=400)

    # validate RPT
    result = keycloak_client.validate_rpt(access_token)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
