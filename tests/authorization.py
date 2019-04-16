#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from .fixtures import keycloak_client


def test_basic_authorization_header(keycloak_client):
    """ Test case for basic_authorization_header """
    authorization = keycloak_client.basic_authorization_header
    assert authorization is not None
    assert authorization == 'Basic Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ=='


@patch('keycloak.authorization.requests.post')
def test_retrieve_rpt(mock_post, keycloak_client):
    """ Test case for retrieve_rpt """
    mock_post.return_value.json = MagicMock()
    payload = {'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket', 'ticket': 'ticket-12345'}
    headers = {'Authorization': 'Bearer access-token-12345'}
    token_endpoint = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/token'
    keycloak_client.retrieve_rpt('access-token-12345', 'ticket-12345')
    mock_post.assert_called_once_with(token_endpoint, data=payload, headers=headers)
    mock_post.return_value.json.assert_called_once()


@patch('keycloak.authorization.requests.post')
def test_validate_rpt(mock_post, keycloak_client):
    """ Test case for validate_rpt """
    mock_post.return_value.json = MagicMock()
    payload = {'token_type_hint': 'requesting_party_token', 'token': 'token123456789'}
    headers = {'Authorization': keycloak_client.basic_authorization_header}
    introspection_endpoint = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/token/introspect'
    keycloak_client.validate_rpt('token123456789')
    mock_post.assert_called_once_with(introspection_endpoint, data=payload, headers=headers)
    mock_post.return_value.json.assert_called_once()
