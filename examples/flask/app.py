#! -*- coding: utf-8 -*-
import os
from flask import Flask
from keycloak.contrib.wsgi.middleware import AuthenticationMiddleware

from blueprints import auth


def _get_keycloak_config_file():
    """
    Method to retrieve the config file path

    Returns:
        str
    """
    current_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_directory, 'keycloak.json')


def _create_app():
    """
    Method to create the basic flask object

    Returns:
        Flask
    """
    app = Flask(__name__)
    return app


def _register_middlewares(app):
    """
    Method to register middlewares

    Args:
        app (Flask): flask app object

    Returns:
        Flask
    """
    return_url = 'http://localhost:5000/'
    config_file = _get_keycloak_config_file()
    app.wsgi_app = AuthenticationMiddleware(app.wsgi_app, return_url, config_file)
    return app


def _register_blueprints(app):
    """
    Method to register blueprints to the flask app

    Args:
        app (Flask): flask app object

    Returns:
        Flask
    """
    app.register_blueprint(auth)
    return app


def create_app():
    """
    Method to create flask app

    Returns:
        Flask
    """
    app = _create_app()
    app = _register_middlewares(app)
    app = _register_blueprints(app)
    return app
