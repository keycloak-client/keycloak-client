#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, patch

from keycloak import KeycloakClient
from keycloak.contrib.wsgi.middleware import AuthenticationMiddleware
from keycloak.contrib.wsgi.middleware.authentication import (
    AatConstants,
    AuthenticationHandler,
    HttpHeaders,
    HttpStatus,
)


@patch('keycloak.contrib.wsgi.middleware.AuthenticationMiddleware.__init__')
def test_middleware_init(mock_init):
    """ Test case for AuthenticationMiddleware.__init__ """
    mock_init.return_value = None
    AuthenticationMiddleware('param-1', 'param-2', 'param-3')
    mock_init.assert_called_once_with('param-1', 'param-2', 'param-3')


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.keycloak_client')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_middleware_call(mock_login, mock_callback, mock_keycloak):
    """ Test case for AuthenticationMiddleware.__call__ """
    mock_app = MagicMock()
    return_url = 'http://return-url.com'
    mock_config = MagicMock()
    mock_start_response = MagicMock()
    middleware = AuthenticationMiddleware(mock_app, return_url, mock_config)
    middleware({'PATH_INFO': '/login-callback'}, mock_start_response)
    mock_callback.assert_called_once()
    middleware({}, mock_start_response)
    mock_login.assert_called_once()


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.is_aat_access_token_valid')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_middleware_other(mock_login, mock_login_callback, mock_token):
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
        (HttpHeaders.LOCATION, 'https://login.com'),
    ]
    mock_start_response.assert_called_once_with(HttpStatus.REDIRECT, headers)
    assert response == [b'Initiating authentication']


@patch('keycloak.contrib.wsgi.middleware.authentication.KeycloakClient')
def test_handler_login_callback(mock_keycloak_client):
    """ Test case for AuthenticationHandler.login_callback """
    mock_environ = MagicMock()
    mock_keycloak_client.return_value.authentication_callback = MagicMock()
    mock_keycloak_client.return_value.authentication_callback.return_value = {'access_token': 'val', 'refresh_token': 'val'}
    mock_start_response = MagicMock()
    handler = AuthenticationHandler(mock_environ, mock_start_response, 'param-1', 'param-2')
    response = handler.login_callback()
    headers = [
        (HttpHeaders.SET_COOKIE, 'AAT_ACCESS_TOKEN=val; Path=/'),
        (HttpHeaders.SET_COOKIE, 'AAT_REFRESH_TOKEN=val; Path=/'),
        (HttpHeaders.LOCATION, 'param-1'),
    ]
    mock_start_response.assert_called_once_with(HttpStatus.REDIRECT, headers)
    assert response == [b'Authentication successful']


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.request')
def test_handler_access_token_valid(mock_request):
    """ Test case for token validity flags """
    mock_request = MagicMock()
    mock_request.return_value.cookies.return_value = {'AAT_ACCESS_TOKEN': 'val', 'AAT_REFRESH_TOKEN': 'val'}
    mock_environ = MagicMock()
    mock_start_response = MagicMock()
    handler = AuthenticationHandler(mock_environ, mock_start_response, 'param-1', 'param-2')
    assert handler.is_aat_access_token_valid == False
    assert handler.is_aat_refresh_token_valid == False


def test_http_headers():
    """ Test case for HttpHeaders """
    assert HttpHeaders.CONTENT_TYPE == 'Content-Type'
    assert HttpHeaders.LOCATION == 'Location'
    assert HttpHeaders.SET_COOKIE == 'Set-Cookie'


def test_http_status():
    """ Test case for HttpHeaders """
    assert HttpStatus.SUCCESS == '200 Ok'
    assert HttpStatus.REDIRECT == '302 Found'


def test_aat_constants():
    """ Test case for AatConstants """
    assert AatConstants.ACCESS_TOKEN == 'AAT_ACCESS_TOKEN'
    assert AatConstants.REFRESH_TOKEN == 'AAT_REFRESH_TOKEN'
