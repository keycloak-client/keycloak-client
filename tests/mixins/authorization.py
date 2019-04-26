#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, patch


def test_basic_auth_header(keycloak_client):
    """ Test case for basic_auth_header """
    authorization = keycloak_client.basic_auth_header
    assert authorization is not None
    assert authorization == {'Authorization': 'Basic Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ=='}


@patch('keycloak.mixins.resource.ResourceMixin.pat', new_callable=PropertyMock)
@patch('keycloak.mixins.authorization.requests.post')
def test_retrieve_ticket(mock_post, mock_pat, keycloak_client):
    """ Test case for retrieve_rpt """
    mock_pat.return_value = {'access_token': 'access-token-12345'}
    mock_post.return_value.json = MagicMock()
    headers = {'Authorization': 'Bearer access-token-12345'}
    token_endpoint = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/authz/protection/permission'
    resources = [
      {
        "resource_id": "bd94ac68-ee19-4c05-a49c-0715ab2232bf",
        "resource_scopes": [
          "class:read"
        ]
      }
    ]
    keycloak_client.retrieve_ticket(resources)
    mock_pat.assert_called_once()
    mock_post.assert_called_once_with(token_endpoint, json=resources, headers=headers)
    mock_post.return_value.json.assert_called_once()

@patch('keycloak.mixins.authorization.requests.post')
def test_retrieve_rpt(mock_post, keycloak_client):
    """ Test case for retrieve_rpt """
    mock_post.return_value.json = MagicMock()
    payload = {'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket', 'ticket': 'ticket-12345'}
    headers = {'Authorization': 'Bearer access-token-12345'}
    token_endpoint = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/token'
    keycloak_client.retrieve_rpt('access-token-12345', 'ticket-12345')
    mock_post.assert_called_once_with(token_endpoint, data=payload, headers=headers)
    mock_post.return_value.json.assert_called_once()


@patch('keycloak.mixins.authorization.requests.post')
def test_validate_rpt(mock_post, keycloak_client):
    """ Test case for validate_rpt """
    mock_post.return_value.json = MagicMock()
    payload = {'token_type_hint': 'requesting_party_token', 'token': 'token123456789'}
    introspection_endpoint = 'https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc/protocol/openid-connect/token/introspect'
    keycloak_client.validate_rpt('token123456789')
    mock_post.assert_called_once_with(introspection_endpoint, data=payload, headers=keycloak_client.basic_auth_header)
    mock_post.return_value.json.assert_called_once()
