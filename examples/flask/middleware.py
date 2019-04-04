#! -*- coding: utf-8 -*-
import json
from flask import Flask, Response
from keycloak.contrib.wsgi.middleware import AuthenticationMiddleware


app = Flask(__name__)
app.wsgi_app = AuthenticationMiddleware(app.wsgi_app, 'http://puthiry-lab.local:5000/', 'keycloak.json')


@app.route('/')
def home():
    return 'Hola!'


@app.route('/info')
def info():
    return 'Info'


if __name__ == '__main__':
    app.run()
