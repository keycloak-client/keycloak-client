#! -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock, PropertyMock

from keycloak import KeycloakClient
from keycloak.contrib.wsgi.middleware import AuthenticationMiddleware
from keycloak.contrib.wsgi.middleware.authentication import HttpHeaders, HttpStatus, AuthenticationHandler


@patch('keycloak.contrib.wsgi.middleware.AuthenticationMiddleware.__init__')
def test_middleware_init(mock_init):
    """ Test case for AuthenticationMiddleware.__init__ """
    mock_init.return_value = None
    AuthenticationMiddleware('param-1', 'param-2', 'param-3')
    mock_init.assert_called_once_with('param-1', 'param-2', 'param-3')


@patch('keycloak.contrib.wsgi.middleware.AuthenticationMiddleware.__call__')
def test_middleware_call(mock_call):
    """ Test case for AuthenticationMiddleware.__call__ """
    middleware = AuthenticationMiddleware('param-1', 'param-2', 'param-3')
    middleware()
    mock_call.assert_called_once()


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_middleware_other(mock_login, mock_login_callback):
    """ Test case for URLS not handled by the middleware """
    mock_app = MagicMock()
    mock_environ = MagicMock()
    mock_start_response = MagicMock()
    middleware = AuthenticationMiddleware(mock_app, 'param-1', 'param-2')
    middleware(mock_environ, mock_start_response)
    mock_login.assert_not_called()
    mock_login_callback.assert_not_called()
    mock_app.assert_called_once_with(mock_environ, mock_start_response)


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.__init__')
def test_handler_init(mock_init):
    """ Test case for AuthenticationHandler.__init__ """
    mock_init.return_value = None
    AuthenticationHandler('param-1', 'param-2', 'param-3', 'param-4')
    mock_init.assert_called_once_with('param-1', 'param-2', 'param-3', 'param-4')


@patch('keycloak.contrib.wsgi.middleware.authentication.Request')
def test_handler_request(mock_request):
    """ Test case for AuthenticationHandler.request """
    handler = AuthenticationHandler('param-1', 'param-2', 'param-3', 'param-4')
    handler.request
    mock_request.assert_called_once_with('param-1')


@patch('keycloak.contrib.wsgi.middleware.authentication.KeycloakClient')
def test_handler_keycloak_client(mock_keycloak_client):
    """ Test case for AuthenticationHandler.keycloak_client """
    handler = AuthenticationHandler('param-1', 'param-2', 'param-3', 'param-4')
    handler.keycloak_client
    mock_keycloak_client.assert_called_once_with(config_file='param-4')


@patch('keycloak.contrib.wsgi.middleware.authentication.KeycloakClient')
def test_handler_login(mock_keycloak_client):
    """ Test case for AuthenticationHandler.login """
    mock_keycloak_client.return_value.authentication_url = 'https://login.com'
    mock_start_response = MagicMock()
    handler = AuthenticationHandler('param-1', mock_start_response, 'param-2', 'param-3')
    response = handler.login()
    headers = [
        (HttpHeaders.CONTENT_TYPE, 'text/html; charset=utf-8'),
        (HttpHeaders.LOCATION, 'https://login.com'),
    ]
    mock_start_response.assert_called_once_with(HttpStatus.REDIRECT, headers)
    assert response == [b'Initiating authentication']


@patch('keycloak.contrib.wsgi.middleware.authentication.KeycloakClient')
def test_handler_login_callback(mock_keycloak_client):
    """ Test case for AuthenticationHandler.login_callback """
    mock_environ = MagicMock()
    mock_keycloak_client.return_value.authentication_callback = MagicMock()
    mock_keycloak_client.return_value.authentication_callback.return_value = {'key': 'val'}
    mock_start_response = MagicMock()
    handler = AuthenticationHandler(mock_environ, mock_start_response, 'param-1', 'param-2')
    response = handler.login_callback()
    headers = [
        (HttpHeaders.CONTENT_TYPE, 'application/json; charset=utf-8'),
        (HttpHeaders.SET_COOKIE, ' keycloak_aat="eyJrZXkiOiAidmFsIn0="; Path=/'),
        (HttpHeaders.LOCATION, 'param-1'),
    ]
    mock_start_response.assert_called_once_with(HttpStatus.REDIRECT, headers)
    assert response == [b'Authentication successful']


def test_http_headers():
    """ Test case for HttpHeaders """
    assert HttpHeaders.CONTENT_TYPE == 'Content-Type'
    assert HttpHeaders.LOCATION == 'Location'
    assert HttpHeaders.SET_COOKIE == 'Set-Cookie'


def test_http_status():
    """ Test case for HttpHeaders """
    assert HttpStatus.SUCCESS == '200 Ok'
    assert HttpStatus.REDIRECT == '302 Found'
