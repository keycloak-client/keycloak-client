# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError
from keycloak.exceptions import AlgorithmNotSupported
from keycloak.utils import basic_auth


@patch("keycloak.mixins.token.requests.get")
def test_keys(mock_get, kc_client, kc_config, monkeypatch):
    """ Test case for keys """
    monkeypatch.setattr(kc_client, "_jwks", [])
    mock_get.return_value.json = MagicMock()
    kc_client.jwks
    mock_get.assert_called_once_with(kc_config.uma2.jwks_uri)
    mock_get.return_value.json.assert_called_once()


def test_jwk(kc_client):
    key = kc_client.fetch_jwk("jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q")
    assert key == json.dumps(
        {
            "kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "gvG6nS5gWCU60KbcjoMScEyo_avU0I1gfnKp-wNzL5n1MU3AexLp4dErafyXhwuHDc1Kx-v76NGykjpgMXTknhxltxJI9wewn6nDSSF6g-Qz08dUCstl3kdkwOXBYPqmbXknSMGTgQ4X94kFR4QeUUf_qdJxKaqB2eGciX5XGb95Z5rPFjH41wgyj_VcuZVfzSKj915PbJAMXEjGUtN-PNfEvF_3SPvRGU3lv-agAGlJrhBdNsnuVmnobgwufYC8XNwK3jkgprBWoH5UU3gUUH0979e8hYAov3wKlRT4X2HQDNrQvlne7ysAIIMp5XmrOctTcmT1AIPe8k0-41s0Xw",
            "e": "AQAB",
        }
    )


@patch("keycloak.mixins.token.b64decode")
def test_parse_key_and_alg(mock_b64decode, kc_client):
    """ Test case for parse_header """
    header_encoded = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqVmFzcjZPR0w1azBWRkJzdWJLdWMzWGdlYWMtQWZwcW9YVkdrbUFhbjRRIn0"
    header_decoded = {
        "kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q",
        "typ": "JWT",
        "alg": "RS256",
    }
    mock_b64decode.return_value = header_decoded
    kc_client.parse_key_and_alg(header_encoded)
    mock_b64decode.assert_called_once_with(header_encoded, deserialize=True)


@patch("keycloak.mixins.token.jwt.decode")
@patch("keycloak.mixins.token.TokenMixin.parse_key_and_alg")
def test_decode(mock_parse_key_and_alg, mock_decode, kc_client, kc_config):
    """ Test case for decode_jwt """
    token = "header.payload.signature"
    mock_parse_key_and_alg.return_value = ("key", "algorithm")
    kc_client.decode(token)
    mock_parse_key_and_alg.assert_called_once_with("header")
    mock_decode.assert_called_once_with(
        token,
        "key",
        algorithms=["algorithm"],
        issuer=kc_config.uma2.issuer,
        audience=kc_config.client.client_id,
    )


def test_construct_key_failure(kc_client):
    with pytest.raises(AlgorithmNotSupported) as ex:
        kc_client.construct_key("unknown", "unknown")
    assert ex.type == AlgorithmNotSupported


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
