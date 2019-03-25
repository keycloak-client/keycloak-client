#! -*- coding: utf-8 -*-
from flask import Flask, request, redirect, jsonify
from keycloak import KeycloakClient


# create keycloak client
keycloak_client = KeycloakClient()


# create flask app
app = Flask(__name__)


@app.route('/login', methods=['GET'])
def login():
    """ Endpoint to initiate login """
    return redirect(keycloak_client.login_url)


@app.route('/callback', methods=['GET'])
def callback():
    """ Endpoint to retrieve user tokens """
    code = request.args.get('code')
    access_token, refresh_token, id_token = keycloak_client.retrieve_tokens(code)
    print(access_token)
    user_info = keycloak_client.get_info(access_token, id_token)
    return jsonify(user_info)


@app.route('/introspect', methods=['POST'])
def introspect():
    """ Endpoint to introspect user tokens """
    request_data = request.get_json()
    access_token = request_data['access_token']
    result = keycloak_client.validate_access_token(access_token)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
