# -*- coding: utf-8 -*-
import json
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
def test_parse_key_and_alg(
    mock_fix_padding, mock_b64decode, mock_json_loads, kc_client, keys
):
    """ Test case for parse_header """
    header_encoded = "eyJraWQiOiAialZhc3I2T0dMNWswVkZCc3ViS3VjM1hnZWFjLUFmcHFvWFZHa21BYW40USIsICJhbGciOiAiUlMyNTYifQo="
    header_decoded = (
        '{"kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q", "alg": "RS256"}'
    )
    header_dict = {"kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q", "alg": "RS256"}
    mock_fix_padding.return_value = header_encoded
    mock_b64decode.return_value = header_decoded
    mock_json_loads.return_value = header_dict
    kc_client._parse_key_and_alg(header_encoded)
    mock_fix_padding.assert_called_once_with(header_encoded)
    mock_b64decode.assert_called_once_with(header_encoded)
    mock_json_loads.assert_called_with(header_decoded)


@patch("keycloak.mixins.jwt.jwt.decode")
@patch("keycloak.mixins.jwt.JWTMixin._parse_key_and_alg")
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
