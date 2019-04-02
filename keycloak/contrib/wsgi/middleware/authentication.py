#! -*- coding: utf-8 -*-

""" middlewares for flask framework """

import json
from base64 import b64encode
from http.cookies import SimpleCookie

from cached_property import cached_property
from werkzeug.wrappers import Request

from keycloak import KeycloakClient


# pylint: disable=too-few-public-methods
class HttpHeaders:
    """ HTTP headers """
    CONTENT_TYPE = 'Content-Type'
    LOCATION = 'Location'
    SET_COOKIE = 'Set-Cookie'


# pylint: disable=too-few-public-methods
class HttpStatus:
    """ HTTP status codes """
    SUCCESS = '200 Ok'
    REDIRECT = '302 Found'


class AuthenticationHandler:
    """ URL handlers associated with the authentication middleware """

    def __init__(self, environ, start_response, keycloak_return_url, keycloak_config_file):
        """
        Method to initialize the object

        Args:
            request (werkzeug.wrappers.Request): werkzeug request object
            start_response (werkzeug.serving.WSGIRequestHandler.start_response): wsgi callable
            keycloak_return_url (str): URL to which the user needs to be redirected after login
            keycloak_config_file (str): keycloak configuration file
        """
        self.environ = environ
        self.start_response = start_response
        self.keycloak_return_url = keycloak_return_url
        self.keycloak_config_file = keycloak_config_file

    @cached_property
    def request(self):
        """ WSGI request """
        return Request(self.environ)

    @cached_property
    def keycloak_client(self):
        """ Keycloak client """
        return KeycloakClient(config_file=self.keycloak_config_file)

    def login(self):
        """ Method to initiate keycloak authentication """

        # prepare headers
        headers = [
            (HttpHeaders.CONTENT_TYPE, 'text/html; charset=utf-8'),
            (HttpHeaders.LOCATION, self.keycloak_client.authentication_url),
        ]

        # start http response
        self.start_response(HttpStatus.REDIRECT, headers)

        # write content
        return [b'Initiaing authentication']

    def login_callback(self):
        """ Keycloak authentication callback handler """

        # retrieve code from the query params
        code = self.request.args.get('code')

        # retrieve aat
        keycloak_aat = self.keycloak_client.authentication_callback(code)

        # encode aat with base64 encoding
        keycloak_aat = json.dumps(keycloak_aat)
        keycloak_aat = keycloak_aat.encode('utf-8')
        keycloak_aat = b64encode(keycloak_aat)
        keycloak_aat = keycloak_aat.decode('utf-8')

        # create cookie and insert aat
        cookie = SimpleCookie()
        cookie['keycloak_aat'] = keycloak_aat
        cookie['keycloak_aat']['path'] = '/'

        # prepare headers
        headers = [
            (HttpHeaders.CONTENT_TYPE, 'application/json; charset=utf-8'),
            (HttpHeaders.SET_COOKIE, cookie.output(header='')),
            (HttpHeaders.LOCATION, self.keycloak_return_url),
        ]

        # start http response
        self.start_response(HttpStatus.REDIRECT, headers)

        # write content
        return [b'Authentication successful']


# pylint: disable=too-few-public-methods
class  AuthenticationMiddleware:
    """ Authentication middelware """

    def __init__(self, app, keycloak_return_url, keycloak_config_file):
        """
        Method to initialize the object

        Args:
            app: WSGI app
            keycloak_return_url (str): URL to which the user needs to be redirected after login
            keycloak_config_file (str): keycloak configuration file
        """
        self.app = app
        self.keycloak_return_url = keycloak_return_url
        self.keycloak_config_file = keycloak_config_file

    def __call__(self, environ, start_response):
        """
        Middleware

        Args:
            environ (dict): CGI environment variables
            start_response (werkzeug.serving.WSGIRequestHandler.start_response): wsgi callable
        """

        # define auth handlers
        auth_handlers = AuthenticationHandler(
            environ,
            start_response,
            self.keycloak_return_url,
            self.keycloak_config_file
        )

        # define the path
        path = environ.get('PATH_INFO', '/')

        # handle login requests
        if path == '/login':
            return auth_handlers.login()

        # handle callback requests
        if path == '/login-callback':
            return auth_handlers.login_callback()

        # handle other requests
        return self.app(environ, start_response)
