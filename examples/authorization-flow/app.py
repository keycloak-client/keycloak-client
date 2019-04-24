#! -*- coding: utf-8 -*-
import json
from flask import Flask, redirect, request, jsonify, Response, render_template
from keycloak import KeycloakClient


api = Flask(__name__)


keycloak_client = KeycloakClient()


@api.route('/login', methods=['GET'])
def login():
    """ Initiate authentication """
    auth_url = keycloak_client.authentication_url()
    return redirect(auth_url)


@api.route('/login/callback', methods=['GET'])
def login_callback():
    """ Authentication callback handler """
    code = request.args.get('code')
    aat = keycloak_client.authentication_callback(code)
    access_token = aat['access_token']
    response = Response('Please open `/student` within the browser')
    response.set_cookie('ACCESS_TOKEN', access_token)
    return response


@api.route('/student', methods=['GET'])
def list_student():
    """ API to fetch the list of students """
    return render_template('list.html')


@api.route('/student', methods=['POST'])
def create_student():
    """ API to create student """
    return 'It worked'


@api.route('/student/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    """ API to update student """
    return 'It worked'


@api.route('/student<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """ API to delete student """
    return 'It worked'


@api.cli.command()
def register_resources():
    """ Command to register resources with the keycloak server """
    keycloak_client.register_resources('resources.json')


def authorization():
    """ Authorization middleware """
    # rules
    with open('permissions.json') as f:
        rules = json.loads(f.read())

    # validate rules
    for path, rule in rules.items():

        if path == request.path:

            # deny
            deny = Response('You do not have access to the requested resource', status=403)

            # read access token
            access_token = request.cookies.get('ACCESS_TOKEN')

            # retrieve RPT
            try:
                rpt = keycloak_client.retrieve_rpt(access_token)['access_token']
                rpt = keycloak_client.decode_jwt(rpt)
            except Exception:
                return deny

            # retrieve permissions
            permissions = rpt.get('authorization', {}).get('permissions')

            _resource = rule['resource']
            _permissions = rule['permissions']
            _scope_required = _permissions[request.method.lower()]

            for permission in permissions:
                resource = permission.get('rsname')
                scopes = permission.get('scopes', [])
                if resource == _resource and _scope_required in scopes:
                    return

            # deny access by default
            return deny


# register middleware
api.before_request(authorization)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
