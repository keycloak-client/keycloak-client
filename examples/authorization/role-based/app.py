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

    return redirect('/student')


@api.route('/student', methods=['GET'])
def list_student():
    """ API to fetch the list of students """
    return 'It worked !!!'


@api.cli.command()
def list_resources():
    """ Command to list resources with the keycloak server """
    resources = keycloak_client.list_resource()
    resources = json.dumps(resources, indent=2)
    print(resources)


@api.cli.command()
def create_resources():
    """ Command to register resources with the keycloak server """
    # read resources
    with open('auth/resources.json') as resources:
        _data = resources.read()
        resources = json.loads(_data)

    # register resource one by one
    for resource in resources:
        keycloak_client.create_resource(resource)


def get_resource_id(resources, name):
    """ Method to find id using name within a set of resources """
    for resource in resources:
        if resource['name'] == name:
            return resource['_id']

@api.cli.command()
def list_policies():
    """ Command to list policies with the keycloak server """
    resources = keycloak_client.list_resource()
    for resource_id in resources:
        print('Fetching policies for resource', resource_id)
        policies = keycloak_client.list_policy(resource_id)
        policies = json.dumps(policies, indent=2)
        print(policies)


@api.cli.command()
def create_policies():
    """ Command to register policies with the keycloak server """
    resources = []

    # read resources
    with open('auth/policies.json') as policy_file:
        policies = policy_file.read()
        policies = json.loads(policies)

    # read all policies
    for resource_id in keycloak_client.list_resource():
        print('Reading resource', resource_id)
        resource = keycloak_client.read_resource(resource_id)
        resources.append(resource)

    # register resource one by one
    for resource_name, resource_policies in policies.items():
        for policy in resource_policies:
            resource_id = get_resource_id(resources, resource_name)
            keycloak_client.create_policy(resource_id, policy)


def role_based_authorization():
    """ Authorization middleware """
    user_roles = []

    # retrieve user roles from token
    access_token = session.get('access_token')
    if access_token:

        # decode access token
        try:
            token_info = keycloak_client.decode_jwt(access_token)
        except Exception:
            del session['access_token']
            return redirect(request.path)

        # read user roles
        user_roles = token_info.get('resource_access', {}) \
                               .get(keycloak_client.config.client_id, {}) \
                               .get('roles', [])

    # read rules
    with open('auth/rules.json') as rules_file:
        rules = rules_file.read()
        rules = json.loads(rules)

    # validate rules
    for path, rule in rules.items():
        if path == request.path:
            if rule[request.method.lower()] not in user_roles:
                return Response(status=403)


# register middleware
api.before_request(role_based_authorization)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
