#! -*- coding: utf-8 -*-
import json
from flask import Flask
from keycloak.contrib.wsgi.middleware import AuthenticationMiddleware


app = Flask(__name__)
app.wsgi_app = AuthenticationMiddleware(app.wsgi_app, '/', 'keycloak.json')


@app.route('/')
def home():
    return 'Hello'


if __name__ == '__main__':
    app.run()
