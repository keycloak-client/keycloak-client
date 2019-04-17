#! -*- coding: utf-8 -*-
import json
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
    aat = keycloak_client.authentication_callback(code)
    return jsonify(aat)


@api.route('/auth/ticket', methods=['POST'])
def auth_ticket():
    """ Generate permission ticket """
    ticket = keycloak_client.retrieve_ticket(resources=request.json)
    return jsonify(ticket)


@api.route('/auth/rpt', methods=['POST'])
def auth_rpt():
    """ Generate RPT (request party token) """
    _, aat = request.headers.get('Authorization').split()
    ticket = request.json.get('ticket')
    rpt = keycloak_client.retrieve_rpt(aat, ticket)
    rpt = keycloak_client.decode_jwt(rpt)
    return jsonify(rpt)


@api.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    """ Retrieve new access token using the existing refresh token """
    refresh_token = request.json.get('refresh_token')
    token = keycloak_client.refresh_access_token(refresh_token)
    return jsonify(token)


@api.cli.command()
def register_resources():
    """ Register resources with the keycloak server """

    # read resouces.json
    with open('resources.json') as f:
        records = json.loads(f.read())

    # define PAT
    pat = keycloak_client.pat['access_token']

    # iterate over resources
    for record in records:

        # parse resource and policies
        resource = record.get('resource')
        policies = record.get('policies')

        # create resource
        resource = keycloak_client.create_resource(resource)

        # create policies
        for policy in policies:
            keycloak_client.create_permission(pat, resource['_id'], policy)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
