#! -*- coding: utf-8 -*-
from flask import Flask, redirect, request, jsonify
from keycloak import KeycloakClient


api = Flask(__name__)
keycloak_client = KeycloakClient()


@api.route('/login', methods=['GET'])
def login():
    """ Initiate authentication """
    return redirect(keycloak_client.authentication_url)


@api.route('/login/callback', methods=['GET'])
def login_callback():
    """ Authentication callback handler """
    code = request.args.get('code')
    response = keycloak_client.authentication_callback(code)
    user_info = keycloak_client.decode_jwt(response['id_token'])
    return jsonify(user_info)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
