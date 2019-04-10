#! -*- coding: utf-8 -*-

""" middlewares for flask framework """

from cached_property import cached_property
from werkzeug.http import dump_cookie
from werkzeug.wrappers import Request

from keycloak import KeycloakClient


# pylint: disable=too-few-public-methods
class AatConstants:
    """ Costants associated with AAT """
    ACCESS_TOKEN = 'AAT_ACCESS_TOKEN'
    REFRESH_TOKEN = 'AAT_REFRESH_TOKEN'


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

    @property
    def is_aat_access_token_valid(self):
        """ Access token valid or not """
        if AatConstants.ACCESS_TOKEN  in self.request.cookies:
            try:
                self.keycloak_client.decode_jwt(self.request.cookies[AatConstants.ACCESS_TOKEN])
                return True
            # pylint: disable=broad-except
            except Exception:
                pass
        return False

    @property
    def is_aat_refresh_token_valid(self):
        """ Refresh token valid or not """
        if AatConstants.REFRESH_TOKEN in self.request.cookies:
            try:
                self.keycloak_client.decode_jwt(self.request.cookies[AatConstants.ACCESS_TOKEN])
                return True
            # pylint: disable=broad-except
            except Exception:
                pass
        return False

    def login(self):
        """ Method to initiate keycloak authentication """

        # prepare headers
        headers = [
            (HttpHeaders.LOCATION, self.keycloak_client.authentication_url),
        ]

        # start http response
        self.start_response(HttpStatus.REDIRECT, headers)

        # write content
        return [b'Initiating authentication']

    def login_callback(self):
        """ Keycloak authentication callback handler """

        # retrieve code from the query params
        code = self.request.args.get('code')

        # retrieve aat
        aat_token = self.keycloak_client.authentication_callback(code)
        access_token = bytes(aat_token['access_token'], 'utf-8')
        refresh_token = bytes(aat_token['refresh_token'], 'utf-8')

        # create cookies
        aat_access_token = dump_cookie(AatConstants.ACCESS_TOKEN, access_token)
        aat_refresh_token = dump_cookie(AatConstants.REFRESH_TOKEN, refresh_token)

        # prepare headers
        headers = [
            (HttpHeaders.SET_COOKIE, aat_access_token),
            (HttpHeaders.SET_COOKIE, aat_refresh_token),
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

        # handle login callback requests
        if path == '/login-callback':
            return auth_handlers.login_callback()

        # initiate login if aat access token is not valid
        if not auth_handlers.is_aat_access_token_valid:
            return auth_handlers.login()

        # handle other requests
        return self.app(environ, start_response)
