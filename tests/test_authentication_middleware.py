#! -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock

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


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.__init__')
def test_handler_init(mock_init):
    """ Test case for AuthenticationHandler.__init__ """
    mock_init.return_value = None
    middleware = AuthenticationMiddleware(MagicMock(), 'param-2', 'param-3')
    middleware({'PATH_INFO': '/other'}, None)
    mock_init.assert_called_once_with({'PATH_INFO': '/other'}, None, 'param-2', 'param-3')


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_handler_login(mock_login, mock_login_callback):
    """ Test case for AuthenticationHandler.login """
    middleware = AuthenticationMiddleware('param-1', 'param-2', 'param-3')
    middleware({'PATH_INFO': '/login'}, None)
    mock_login.assert_called_once()
    mock_login_callback.assert_not_called()


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_handler_login_callback(mock_login, mock_login_callback):
    """ Test case for AuthenticationHandler.login_callback """
    middleware = AuthenticationMiddleware('param-1', 'param-2', 'param-3')
    middleware({'PATH_INFO': '/login-callback'}, None)
    mock_login.assert_not_called()
    mock_login_callback.assert_called_once()


@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login_callback')
@patch('keycloak.contrib.wsgi.middleware.authentication.AuthenticationHandler.login')
def test_handler_other(mock_login, mock_login_callback):
    """ Test case for other uris """
    middleware = AuthenticationMiddleware(MagicMock(), 'param-2', 'param-3')
    middleware({'PATH_INFO': '/other'}, None)
    mock_login.assert_not_called()
    mock_login_callback.assert_not_called()


def test_http_headers():
    """ Test case for HttpHeaders """
    assert HttpHeaders.CONTENT_TYPE == 'Content-Type'
    assert HttpHeaders.LOCATION == 'Location'
    assert HttpHeaders.SET_COOKIE == 'Set-Cookie'


def test_http_status():
    """ Test case for HttpHeaders """
    assert HttpStatus.SUCCESS == '200 Ok'
    assert HttpStatus.REDIRECT == '302 Found'
