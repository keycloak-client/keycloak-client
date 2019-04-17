#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, patch


@patch('keycloak.mixins.permission.requests.get')
def test_list_permission(mock_get, keycloak_client):
    """ Test case for list permission """
    aat = 'access-token-12345'
    headers = {'Authorization': 'Bearer access-token-12345'}
    mock_get.return_value.json = MagicMock()
    keycloak_client.list_permission(aat)
    mock_get.assert_called_once_with(keycloak_client.config.policy_endpoint, headers=headers)
    mock_get.return_value.json.assert_called_once()


@patch('keycloak.mixins.permission.requests.post')
def test_create_permission(mock_post, keycloak_client):
    """ Test case to create permission """
    aat = 'access-token-12345'
    resource_id = 'resource-12345'
    permission = {
        "name": "Any people manager",
        "description": "Allow access to any people manager",
        "scopes": ["read"],
        "clients": ["my-client"]
    }
    headers = {'Authorization': 'Bearer access-token-12345'}
    endpoint = keycloak_client.config.policy_endpoint + '/' + resource_id
    mock_post.return_value.json = MagicMock()
    keycloak_client.create_permission(aat, resource_id, permission)
    mock_post.assert_called_once_with(endpoint, json=permission, headers=headers)
    mock_post.return_value.json.assert_called_once()


@patch('keycloak.mixins.permission.requests.put')
def test_update_permission(mock_put, keycloak_client):
    """ Test case to update permission """
    aat = 'access-token-12345'
    permission_id = 'permission-12345'
    permission = {
        "name": "Any people manager",
        "description": "Allow access to any people manager",
        "scopes": ["read"],
        "clients": ["my-client"]
    }
    headers = {'Authorization': 'Bearer access-token-12345'}
    endpoint = keycloak_client.config.policy_endpoint + '/' + permission_id
    keycloak_client.update_permission(aat, permission_id, permission)
    mock_put.assert_called_once_with(endpoint, json=permission, headers=headers)


@patch('keycloak.mixins.permission.requests.delete')
def test_delete_permission(mock_delete, keycloak_client):
    """ Test case for delete permission """
    aat = 'access-token-12345'
    permission_id = 'permission-12345'
    headers = {'Authorization': 'Bearer access-token-12345'}
    endpoint = keycloak_client.config.policy_endpoint + '/' + permission_id
    keycloak_client.delete_permission(aat, permission_id)
    mock_delete.assert_called_once_with(endpoint, headers=headers)
