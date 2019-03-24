#! -*- coding: utf-8 -*-
from flask import Flask, request, redirect, jsonify
from keycloak import KeycloakClient


# create keycloak client
keycloak_client = KeycloakClient()


# create flask app
app = Flask(__name__)


@app.route('/login')
def login():
    """ Endpoint to initiate login """
    return redirect(keycloak_client.login_url)


@app.route('/callback')
def callback():
    """ Endpoint to retrieve user tokens """
    code = request.args.get('code')
    access_token, refresh_token, id_token = keycloak_client.retrieve_tokens(code)
    access_token_info = keycloak_client.get_access_token_info(access_token)
    id_token_info = keycloak_client.get_id_token_info(id_token)
    return jsonify({
        'access_token_info': access_token_info,
        'id_token_info': id_token_info,
    })


if __name__ == '__main__':
    app.run(debug=True)
