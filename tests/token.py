#! -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, PropertyMock, patch


@patch('keycloak.mixins.token.requests.get')
def test_keys(mock_get, keycloak_client):
    """ Test case for keys """
    mock_get.return_value.json = MagicMock()
    keycloak_client.keys
    mock_get.assert_called_once_with(keycloak_client.config.jwks_uri)
    mock_get.return_value.json.assert_called_once()


@patch('keycloak.mixins.token.json.loads')
@patch('keycloak.mixins.token.base64.b64decode')
@patch('keycloak.mixins.token.fix_padding')
def test_parse_header(mock_fix_padding, mock_b64decode, mock_loads, keycloak_client):
    """ Test case for parse_header """
    mock_fix_padding.return_value = 'Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ'
    mock_b64decode.return_value = '{"key":"value"}'
    keycloak_client.parse_header('Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ')
    mock_fix_padding.assert_called_once_with('Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ')
    mock_b64decode.assert_called_once_with('Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ')
    mock_loads.assert_called_once_with('{"key":"value"}')


@patch('keycloak.mixins.token.jwt.algorithms.RSAAlgorithm.from_jwk')
@patch('keycloak.mixins.token.JwtMixin.keys', new_callable=PropertyMock)
def test_get_signing_key(mock_keys, mock_rsa, keycloak_client):
    """ Test case for get_signing_key """
    key_info = {'kid': '123456789', 'alg': 'RS256'}
    mock_keys.return_value = [{'kid': '123456789', 'alg': 'RS256'}]
    signing_key = keycloak_client.get_signing_key(key_info)
    mock_keys.assert_called_once()
    mock_rsa.assert_called_once_with(json.dumps(key_info))


def test_get_signing_algorithm(keycloak_client):
    """ Test case for get_signing_algorithm """
    jwt_header = {'alg': 'RS256'}
    algorithm = keycloak_client.get_signing_algorithm(jwt_header)
    assert algorithm == jwt_header['alg']


@patch('keycloak.mixins.token.jwt.decode')
@patch('keycloak.mixins.token.JwtMixin.get_signing_algorithm')
@patch('keycloak.mixins.token.JwtMixin.get_signing_key')
@patch('keycloak.mixins.token.JwtMixin.parse_header')
def test_decode_jwt(mock_parse_header, mock_get_signing_key, mock_get_signing_algorithm, mock_decode, keycloak_client):
    """ Test case for decode_jwt """
    token = 'header.payload.signature'
    mock_parse_header.return_value = 'header'
    mock_get_signing_key.return_value = 'signing_key'
    mock_get_signing_algorithm.return_value = 'signing_algorithm'
    options = {'verify_aud': False, 'verify_iss': False}
    keycloak_client.decode_jwt(token)
    mock_parse_header.assert_called_once_with('header')
    mock_get_signing_key.assert_called_once_with('header')
    mock_get_signing_algorithm.assert_called_once_with('header')
    mock_decode.assert_called_once_with(token, 'signing_key', algorithms=['signing_algorithm'], options=options)


@patch('keycloak.mixins.token.requests.post')
def test_refresh_access_token(mock_post, keycloak_client):
    """ Test case for refresh_access_token """
    token = 'header.payload.signature'
    keycloak_client.refresh_access_token(token)
    mock_post.assert_called_once()
