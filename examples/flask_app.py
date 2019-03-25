#! -*- coding: utf-8 -*-
from keycloak import KeycloakClient
from flask import Flask, request, redirect, jsonify


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


@app.route('/retrieve-pat', methods=['GET'])
def retrieve_pat():
    """ Endpoint to retrieve protection api token (PAT) """
    return jsonify(keycloak_client.pat)


@app.route('/create-resource', methods=['GET'])
def create_resource():
    """ Endpoint to create resource """
    result = keycloak_client.create_resource(
        'Containers',
        ['/containers/*', '/con/*'],
        ['create', 'read', 'update', 'delete']
    )
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
