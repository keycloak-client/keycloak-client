#! -*- coding: utf-8 -*-
import json
from flask import Flask, redirect, request, session, Response, render_template
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

    # retrieve tokens
    response = keycloak_client.authentication_callback(code)
    session['access_token'] = response['access_token']

    return Response('Please open `/student` within the browser')


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
            access_token = session['access_token']

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
