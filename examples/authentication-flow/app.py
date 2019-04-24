#! -*- coding: utf-8 -*-
from flask import Flask, redirect, request, jsonify, session, Response
from keycloak import KeycloakClient


api = Flask(__name__)
api.config['SECRET_KEY'] = 'EYxuFcNqGamVU78GgfupoO5N4z2xokA58XtL0ag'
keycloak_client = KeycloakClient()


@api.route('/login', methods=['GET'])
def login():
    """ Initiate authentication """
    auth_url, state = keycloak_client.authentication_url()
    session[state] = True
    return redirect(auth_url)


@api.route('/login/callback', methods=['GET'])
def login_callback():
    """ Authentication callback handler """
    code = request.args.get('code')
    state = request.args.get('state', 'unknown')

    # validate state
    _session = session.pop(state, None)
    if not _session:
        return Response('Invalid state', status=403)

    # retrieve user info
    response = keycloak_client.authentication_callback(code)
    user_info = keycloak_client.decode_jwt(response['id_token'])

    return jsonify(user_info)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
