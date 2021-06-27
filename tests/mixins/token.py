# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from keycloak.utils import basic_auth


@patch("keycloak.mixins.token.jwt.decode")
def test_decode(mock_decode, kc_client, kc_config):
    """Test case for decode"""
    token = "header.payload.signature"
    kc_client.decode(token)
    mock_decode.assert_called_once_with(
        token,
        kc_client.jwks,
        issuer=kc_config.openid.issuer,
        audience=kc_config.client.client_id,
    )


def test_tokens_setter(kc_client):
    kc_client.tokens = {"name": "akhil"}
    assert kc_client._tokens == {"name": "akhil"}


def test_access_token(kc_client):
    kc_client._tokens = {"access_token": "0123456789", "expires_in": "30"}
    assert kc_client.access_token == "0123456789"


@patch("keycloak.mixins.authorization.AuthorizationMixin.pat")
def test_tokens_valid(mock_pat, kc_client):
    kc_client._tokens = {}
    tokens = {"token": "token0123456789", "expires_in": "30"}
    mock_pat.return_value = tokens
    assert kc_client.tokens == tokens
    mock_pat.assert_called_once_with(None, None)


@patch("keycloak.mixins.token.log.debug")
@patch("keycloak.mixins.token.requests.post")
@patch("keycloak.mixins.token.basic_auth")
def test_refresh_tokens_success(mock_auth, mock_post, mock_debug, kc_client, kc_config):
    headers = basic_auth(kc_config.client.client_id, kc_config.client.client_secret)
    mock_auth.return_value = headers
    kc_client.tokens = {"refresh_token": "token0123456789"}
    kc_client.refresh_tokens()
    payload = {
        "client_id": kc_config.client.client_id,
        "grant_type": "refresh_token",
        "refresh_token": "token0123456789",
    }
    mock_auth.assert_called_once_with(
        kc_config.client.client_id, kc_config.client.client_secret
    )
    mock_post.assert_called_once_with(
        kc_config.uma2.token_endpoint, data=payload, headers=headers
    )
    assert mock_debug.call_count == 2


@patch("keycloak.mixins.token.log.exception")
@patch("keycloak.mixins.token.requests.post")
@patch("keycloak.mixins.token.basic_auth")
def test_refresh_tokens_failure(
    mock_auth, mock_post, mock_exception, kc_client, kc_config
):
    headers = basic_auth(kc_config.client.client_id, kc_config.client.client_secret)
    mock_auth.return_value = headers
    mock_post.return_value.content = "server error"
    mock_post.return_value.raise_for_status = MagicMock(side_effect=HTTPError)
    kc_client.tokens = {"refresh_token": "token0123456789"}
    with pytest.raises(HTTPError) as ex:
        kc_client.refresh_tokens()
    payload = {
        "client_id": kc_config.client.client_id,
        "grant_type": "refresh_token",
        "refresh_token": "token0123456789",
    }
    mock_auth.assert_called_once_with(
        kc_config.client.client_id, kc_config.client.client_secret
    )
    mock_post.assert_called_once_with(
        kc_config.uma2.token_endpoint, data=payload, headers=headers
    )
