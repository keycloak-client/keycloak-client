import json
import base64
import requests
from urllib.parse import urlencode
from flask import Flask, request, redirect


# create flask app
app = Flask(__name__)


@app.route('/login')
def login():
    """ Endpoint to initiate login """
    arguments = urlencode({
        'client_id': 'flask-app',
        'state': 'state123456789',
        'response_type': 'code',
        'scope': 'openid profile client_roles',
        'redirect_uri': 'http://localhost:5000/callback',
    })
    auth_uri = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/auth'
    endpoint = auth_uri + '?' + arguments
    return redirect(endpoint)


def fix_padding(data):
    """ correct padding for base64 encoding """
    required_padding = len(data) % 4
    return data + ('=' * required_padding)


@app.route('/callback')
def callback():
    """ Endpoint to retrieve logged in user info """
    code = request.args.get('code')
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': 'flask-app',
        'redirect_uri': 'http://localhost:5000/callback',
        'client_secret': '1f49f057-bbf9-4389-a90f-3c5972f5564a'
    }
    token_uri = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/token'
    response = requests.post(token_uri, data=data)
    response.raise_for_status()
    user_tokens = response.json()
    _, access_info, _ = user_tokens['access_token'].split('.')
    _, user_info, _ = user_tokens['id_token'].split('.')
    access_info = fix_padding(access_info)
    user_info = fix_padding(user_info)
    return json.dumps({
        'access_info': json.loads(base64.b64decode(access_info)),
        'user_info': json.loads(base64.b64decode(user_info)),
    })


if __name__ == '__main__':
    app.run(debug=True)
