# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urlencode

import pytest
from requests.exceptions import HTTPError

from keycloak.utils import auth_header


@patch("keycloak.core.authentication.uuid4")
def test_kc_login(mock_uuid4, kc_client, kc_config):
    """Test case for authentication_url"""
    mock_uuid4.return_value = MagicMock()
    mock_uuid4.return_value.hex = "b8862dbe18214fa89cc7cfde8af26b98"
    arguments = urlencode(
        {
            "state": "b8862dbe18214fa89cc7cfde8af26b98",
            "client_id": kc_config.client.client_id,
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": kc_client.callback_uri,
        }
    )
    login_url = f"{kc_config.openid.authorization_endpoint}?{arguments}"
    _login_url, _ = kc_client.login()
    assert login_url == _login_url


@patch("keycloak.core.authentication.httpx.post")
def test_kc_logout(mock_post, kc_client, kc_config):
    kc_client.logout("access-token", "refresh-token")
    payload = {
        "client_id": kc_config.client.client_id,
        "client_secret": kc_config.client.client_secret,
        "refresh_token": "refresh-token",
    }
    headers = auth_header("access-token")
    mock_post.assert_called_once_with(
        kc_config.openid.end_session_endpoint, data=payload, headers=headers
    )


@patch("keycloak.core.authentication.httpx.post")
def test_kc_callback(mock_post, kc_client, kc_config):
    """Test case for authentication_callback"""
    mock_post.return_value.json = MagicMock()
    payload = {
        "code": "code123456789",
        "grant_type": "authorization_code",
        "client_id": kc_config.client.client_id,
        "redirect_uri": kc_client.callback_uri,
        "client_secret": kc_config.client.client_secret,
    }
    kc_client.callback(code="code123456789")
    mock_post.assert_called_once_with(kc_config.openid.token_endpoint, data=payload)
    mock_post.return_value.json.assert_called_once()


@patch("keycloak.core.authentication.httpx.post")
def test_kc_callback_failure(mock_post, kc_client, kc_config):
    mock_post.return_value = MagicMock()
    mock_post.return_value.content = "server error"
    mock_post.return_value.raise_for_status = MagicMock(side_effect=HTTPError)
    payload = {
        "code": "code123456789",
        "grant_type": "authorization_code",
        "client_id": kc_config.client.client_id,
        "redirect_uri": kc_client.callback_uri,
        "client_secret": kc_config.client.client_secret,
    }
    with pytest.raises(HTTPError) as ex:
        kc_client.callback(code="code123456789")
    assert ex.type == HTTPError
    mock_post.assert_called_once_with(kc_config.openid.token_endpoint, data=payload)


@patch("keycloak.core.authentication.httpx.post")
@patch("keycloak.core.authentication.httpx.get")
def test_kc_userinfo(mock_httpx_get, mock_httpx_post, kc_client):
    mock_httpx_get.return_value.json = MagicMock()
    kc_client.userinfo
    mock_httpx_get.assert_called()
    mock_httpx_get.return_value.json.assert_called()


@patch("keycloak.core.authentication.httpx.get")
def test_kc_fetch_userinfo(mock_post, kc_client, kc_config):
    mock_post.return_value.json = MagicMock()
    token = "token123456789"
    headers = auth_header(token)
    kc_client.fetch_userinfo(token)
    mock_post.assert_called_once_with(
        kc_config.openid.userinfo_endpoint, headers=headers
    )
    mock_post.return_value.json.assert_called_once()


@patch("keycloak.core.authentication.httpx.get")
def test_kc_userinfo_failure(mock_post, kc_client, kc_config):
    mock_post.return_value = MagicMock()
    mock_post.return_value.content = "server error"
    mock_post.return_value.raise_for_status = MagicMock(side_effect=HTTPError)
    token = "token123456789"
    headers = auth_header(token)
    with pytest.raises(HTTPError) as ex:
        kc_client.fetch_userinfo(token)
    assert ex.type == HTTPError
    mock_post.assert_called_once_with(
        kc_config.openid.userinfo_endpoint, headers=headers
    )
