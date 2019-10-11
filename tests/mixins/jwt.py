# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch


@patch("keycloak.mixins.jwt.requests.get")
def test_keys(mock_get, kc_client, kc_config):
    """ Test case for keys """
    mock_get.return_value.json = MagicMock()
    kc_client._keys
    mock_get.assert_called_once_with(kc_config.uma2.jwks_uri)
    mock_get.return_value.json.assert_called_once()


@patch("keycloak.mixins.jwt.json.loads")
@patch("keycloak.mixins.jwt.base64.b64decode")
@patch("keycloak.mixins.jwt.fix_padding")
def test_parse_key_and_alg(mock_fix_padding, mock_b64decode, mock_loads, kc_client):
    """ Test case for parse_header """
    mock_fix_padding.return_value = (
        "Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ"
    )
    mock_b64decode.return_value = '{"key":"value"}'
    kc_client._parse_key_and_alg(
        "Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ"
    )
    mock_fix_padding.assert_called_once_with(
        "Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ"
    )
    mock_b64decode.assert_called_once_with(
        "Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ"
    )
    mock_loads.assert_called_with('{"key":"value"}')


@patch("keycloak.mixins.jwt.jwt.decode")
@patch("keycloak.mixins.jwt.JWTMixin._parse_key_and_alg")
def test_decode(mock_parse_key_and_alg, mock_decode, kc_client, kc_config):
    """ Test case for decode_jwt """
    token = "header.payload.signature"
    mock_parse_key_and_alg.return_value = ("header", "key", "algorithm")
    kc_client.decode(token)
    mock_parse_key_and_alg.assert_called_once_with("header")
    mock_decode.assert_called_once_with(
        token,
        "key",
        algorithms=["algorithm"],
        issuer=kc_config.uma2.issuer,
        audience=kc_config.client.client_id,
    )
