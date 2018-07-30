import requests

from flask import Flask, g, request, Response
from flask_oidc import OpenIDConnect

# create flask app
app = Flask(__name__)
app.config.update({
    'TESTING': True,
    'DEBUG': True,
    'SECRET_KEY': '8896958076629c1711b991c4552e8c6616b9e2a94a2fcb7c038fd10b049f30ce',
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'flask-demo',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_VALID_ISSUERS': ['http://keycloak.dev.lti-mosaic.com/auth/realms/demo-env']
})


# create openid client
oidc = OpenIDConnect(app)


@app.route('/login')
@oidc.require_login
def home():

    # fetch user information
    user_info = oidc.user_getinfo(['email', 'sub', 'profile'])
    return 'Email id of the logged in user is: {}'.format(user_info.get('email'))


@app.route('/profiling')
@oidc.require_login
def protected():

    # fetch user information
    user_info = oidc.user_getinfo(['email', 'sub', 'profile'])

    # fetch access token
    payload = {'client_id': 'flask-app', 'grant_type': 'client_credentials', 'client_secret': '53d6d03b-1111-40ab-b308-12b43ef8eaf0'}
    access_token = requests.post('http://keycloak.dev.lti-mosaic.com/auth/realms/demo-env/protocol/openid-connect/token', data=payload).json().get('access_token')

    # permission checking
    payload = {"resources":[{"uri": request.path}], "userId": user_info.get('sub')}
    headers = {"Authorization": "Bearer {}".format(access_token)}
    result = requests.post('http://keycloak.dev.lti-mosaic.com/auth/admin/realms/demo-env/clients/bca0a1d5-7d5e-4d39-aa91-b95f432a6be8/authz/resource-server/policy/evaluate', json=payload, headers=headers).json().get('status')
    if result != 'PERMIT':
        return Response("You are doomed", status=401)

    # process the request
    return 'Howdy'


if __name__ == '__main__':
    app.run()
