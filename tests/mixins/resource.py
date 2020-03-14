# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock

import pytest
from requests.exceptions import HTTPError


@patch("keycloak.mixins.resource.requests.get")
@patch("keycloak.mixins.resource.auth_header")
def test_resources(mock_auth_header, mock_get, kc_client, kc_config):
    token = "token123456789"
    header = {"Authorization": token}
    mock_auth_header.return_value = header
    kc_client.find_resources(token)
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(
        kc_config.uma2.resource_registration_endpoint, headers=header
    )


@patch("keycloak.mixins.resource.requests.get")
@patch("keycloak.mixins.resource.auth_header")
def test_resources_failure(mock_auth_header, mock_get, kc_client, kc_config):
    mock_get.return_value = MagicMock()
    mock_get.return_value.content = "server error"
    mock_get.return_value.raise_for_status = MagicMock(side_effect=HTTPError)
    token = "token123456789"
    header = {"Authorization": token}
    mock_auth_header.return_value = header
    with pytest.raises(HTTPError) as ex:
        kc_client.find_resources(token)
    assert ex.type == HTTPError
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(
        kc_config.uma2.resource_registration_endpoint, headers=header
    )


@patch("keycloak.mixins.resource.requests.get")
@patch("keycloak.mixins.resource.auth_header")
def test_resource(mock_auth_header, mock_get, kc_client, kc_config):
    token = "token123456789"
    resource = "resource123456789"
    header = {"Authorization": token}
    endpoint = f"{kc_config.uma2.resource_registration_endpoint}/{resource}"
    mock_auth_header.return_value = header
    kc_client.find_resource(resource, token)
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(endpoint, headers=header)


@patch("keycloak.mixins.resource.requests.get")
@patch("keycloak.mixins.resource.auth_header")
def test_resource_failure(mock_auth_header, mock_get, kc_client, kc_config):
    mock_get.return_value = MagicMock()
    mock_get.return_value.content = "server error"
    mock_get.return_value.raise_for_status = MagicMock(side_effect=HTTPError)
    token = "token123456789"
    resource = "resource123456789"
    header = {"Authorization": token}
    endpoint = f"{kc_config.uma2.resource_registration_endpoint}/{resource}"
    mock_auth_header.return_value = header
    with pytest.raises(HTTPError) as ex:
        kc_client.find_resource(resource, token)
    assert ex.type == HTTPError
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(endpoint, headers=header)
