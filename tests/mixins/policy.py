#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, patch


@patch('keycloak.mixins.resource.ResourceMixin.pat_auth_header', new_callable=PropertyMock)
@patch('keycloak.mixins.policy.requests.get')
def test_list_policy(mock_get, mock_pat_auth_header, keycloak_client):
    """ Test case for list permission """
    resource = 'resource-12345'
    endpoint = keycloak_client.config.policy_endpoint + '?resource=' + resource
    headers = {'Authorization': 'Bearer access-token-12345'}
    mock_pat_auth_header.return_value = headers
    mock_get.return_value.json = MagicMock()
    keycloak_client.list_policy(resource)
    mock_get.assert_called_once_with(endpoint, headers=headers)
    mock_get.return_value.json.assert_called_once()
    mock_pat_auth_header.assert_called_once()


@patch('keycloak.mixins.resource.ResourceMixin.pat_auth_header', new_callable=PropertyMock)
@patch('keycloak.mixins.policy.requests.post')
def test_create_policy(mock_post, mock_pat_auth_header, keycloak_client):
    """ Test case to create permission """
    resource_id = 'resource-12345'
    permission = {
        "name": "Any people manager",
        "description": "Allow access to any people manager",
        "scopes": ["read"],
        "clients": ["my-client"]
    }
    headers = {'Authorization': 'Bearer access-token-12345'}
    mock_pat_auth_header.return_value = headers
    endpoint = keycloak_client.config.policy_endpoint + '/' + resource_id
    mock_post.return_value.json = MagicMock()
    keycloak_client.create_policy(resource_id, permission)
    mock_post.assert_called_once_with(endpoint, json=permission, headers=headers)
    mock_post.return_value.json.assert_called_once()
    mock_pat_auth_header.assert_called_once()


@patch('keycloak.mixins.resource.ResourceMixin.pat_auth_header', new_callable=PropertyMock)
@patch('keycloak.mixins.policy.requests.put')
def test_update_policy(mock_put, mock_pat_auth_header, keycloak_client):
    """ Test case to update permission """
    permission_id = 'permission-12345'
    permission = {
        "name": "Any people manager",
        "description": "Allow access to any people manager",
        "scopes": ["read"],
        "clients": ["my-client"]
    }
    headers = {'Authorization': 'Bearer access-token-12345'}
    mock_pat_auth_header.return_value = headers
    endpoint = keycloak_client.config.policy_endpoint + '/' + permission_id
    keycloak_client.update_policy(permission_id, permission)
    mock_put.assert_called_once_with(endpoint, json=permission, headers=headers)
    mock_pat_auth_header.assert_called_once()


@patch('keycloak.mixins.resource.ResourceMixin.pat_auth_header', new_callable=PropertyMock)
@patch('keycloak.mixins.policy.requests.delete')
def test_delete_policy(mock_delete, mock_pat_auth_header, keycloak_client):
    """ Test case for delete permission """
    permission_id = 'permission-12345'
    headers = {'Authorization': 'Bearer access-token-12345'}
    mock_pat_auth_header.return_value = headers
    endpoint = keycloak_client.config.policy_endpoint + '/' + permission_id
    keycloak_client.delete_policy(permission_id)
    mock_delete.assert_called_once_with(endpoint, headers=headers)
    mock_pat_auth_header.assert_called_once()
