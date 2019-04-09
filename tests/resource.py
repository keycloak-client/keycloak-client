#! -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, patch

from .fixtures import keycloak_client


@patch('keycloak.resource.requests.post')
def test_pat(mock_post, keycloak_client):
    """ Test case for PAT """
    mock_post.return_value.json = MagicMock()
    payload = {'grant_type': 'client_credentials'}
    headers = {'Authorization': 'Basic Zmxhc2stYXBwOjFmNDlmMDU3LWJiZjktNDM4OS1hOTBmLTNjNTk3MmY1NTY0YQ=='}
    keycloak_client.pat
    mock_post.assert_called_once_with(keycloak_client.config.token_endpoint, data=payload, headers=headers)
    mock_post.return_value.json.assert_called_once()


@patch('keycloak.resource.ResourceMixin.pat', new_callable=PropertyMock)
def test_headers(mock_pat, keycloak_client):
    """ Test case for headers """
    mock_pat.return_value = {'access_token': 'token123456789'}
    headers = {'Authorization': 'Bearer token123456789'}
    result = keycloak_client.headers
    assert result == headers
    mock_pat.assert_called_once()


@patch('keycloak.resource.requests.get')
@patch('keycloak.resource.ResourceMixin.headers', new_callable=PropertyMock)
def test_list_resource(mock_headers, mock_get, keycloak_client):
    """ Test case for list_resource """
    headers = {'Authorization': 'token123456789'}
    mock_headers.return_value = headers
    mock_get.return_value.json = MagicMock()
    keycloak_client.list_resource()
    mock_get.assert_called_once_with(keycloak_client.config.resource_endpoint, headers=headers)
    mock_get.return_value.json.assert_called_once()


@patch('keycloak.resource.requests.post')
@patch('keycloak.resource.ResourceMixin.headers', new_callable=PropertyMock)
def test_create_resource(mock_headers, mock_post, keycloak_client):
    """ Test case for list_resource """
    resource = {}
    headers = {'Authorization': 'token123456789'}
    mock_headers.return_value = headers
    mock_post.return_value.json = MagicMock()
    keycloak_client.create_resource(resource)
    mock_post.assert_called_once_with(keycloak_client.config.resource_endpoint, json=resource, headers=headers)
    mock_post.return_value.json.assert_called_once()


@patch('keycloak.resource.requests.get')
@patch('keycloak.resource.ResourceMixin.headers', new_callable=PropertyMock)
def test_read_resource(mock_headers, mock_get, keycloak_client):
    """ Test case for list_resource """
    resource_id = '123456789'
    headers = {'Authorization': 'token123456789'}
    endpoint = keycloak_client.config.resource_endpoint + resource_id
    mock_headers.return_value = headers
    mock_get.return_value.json = MagicMock()
    keycloak_client.read_resource(resource_id)
    mock_get.assert_called_once_with(endpoint, headers=headers)
    mock_get.return_value.json.assert_called_once()


@patch('keycloak.resource.requests.put')
@patch('keycloak.resource.ResourceMixin.headers', new_callable=PropertyMock)
def test_update_resource(mock_headers, mock_put, keycloak_client):
    """ Test case for list_resource """
    resource_id = '123456789'
    resource = {}
    headers = {'Authorization': 'token123456789'}
    endpoint = keycloak_client.config.resource_endpoint + resource_id
    mock_headers.return_value = headers
    mock_put.return_value.json = MagicMock()
    keycloak_client.update_resource(resource_id, resource)
    mock_put.assert_called_once_with(endpoint, json=resource, headers=headers)
    mock_put.return_value.json.assert_called_once()


@patch('keycloak.resource.requests.delete')
@patch('keycloak.resource.ResourceMixin.headers', new_callable=PropertyMock)
def test_delete_resource(mock_headers, mock_delete, keycloak_client):
    """ Test case for list_resource """
    resource_id = '123456789'
    headers = {'Authorization': 'token123456789'}
    endpoint = keycloak_client.config.resource_endpoint + resource_id
    mock_headers.return_value = headers
    mock_delete.return_value.json = MagicMock()
    keycloak_client.delete_resource(resource_id)
    mock_delete.assert_called_once_with(endpoint, headers=headers)
    mock_delete.return_value.json.assert_called_once()
