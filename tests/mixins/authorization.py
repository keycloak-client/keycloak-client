# -*- coding: utf-8 -*-
from unittest.mock import patch

from keycloak.constants import GrantTypes, TokenType, TokenTypeHints


def test_payload_for_client(kc_client):
    payload = kc_client.payload_for_client()
    assert payload == {"grant_type": GrantTypes.client_credentials}


def test_payload_for_user(kc_client):
    payload = kc_client.payload_for_user("akhilputhiry", "p@$$w0rd")
    assert payload == {
        "grant_type": GrantTypes.password,
        "username": "akhilputhiry",
        "password": "p@$$w0rd",
    }


def test_payload_for_user_empty(kc_client):
    payload = kc_client.payload_for_user()
    assert payload == {}


@patch("keycloak.mixins.authorization.requests.post")
@patch("keycloak.mixins.authorization.AuthorizationMixin.payload_for_client")
@patch("keycloak.mixins.authorization.AuthorizationMixin.payload_for_user")
@patch("keycloak.mixins.authorization.basic_auth")
def test_pat(
    mock_auth_header,
    mock_payload_user,
    mock_payload_client,
    mock_post,
    kc_client,
    kc_config,
):
    token = "token123456789"
    header = {"Authorization": token}
    payload = {"grant_type": GrantTypes.client_credentials}
    mock_auth_header.return_value = header
    mock_payload_user.return_value = None
    mock_payload_client.return_value = payload
    kc_client.pat()
    mock_auth_header.assert_called_once_with(
        kc_config.client.client_id, kc_config.client.client_secret
    )
    mock_payload_user.assert_called_once_with(None, None)
    mock_payload_client.assert_called_once()
    mock_post.assert_called_once_with(
        kc_config.uma2.token_endpoint, data=payload, headers=header
    )


@patch("keycloak.mixins.authorization.requests.post")
@patch("keycloak.mixins.authorization.auth_header")
def test_ticket(mock_auth_header, mock_post, kc_client, kc_config):
    token = "token123456789"
    header = {"Authorization": token}
    resources = [{"resource_id": "id123456789"}]
    mock_auth_header.return_value = header
    kc_client.ticket(resources, token)
    mock_auth_header.assert_called_once_with(token, TokenType.bearer)
    mock_post.assert_called_once_with(
        kc_config.uma2.permission_endpoint, json=resources, headers=header
    )


@patch("keycloak.mixins.authorization.requests.post")
@patch("keycloak.mixins.authorization.auth_header")
def test_rpt(mock_auth_header, mock_post, kc_client, kc_config):
    ticket = "ticket123456789"
    token = "token123456789"
    header = {"Authorization": token}
    payload = {"grant_type": GrantTypes.uma_ticket, "ticket": ticket}
    mock_auth_header.return_value = header
    kc_client.rpt(ticket, token)
    mock_auth_header.assert_called_once_with(token, TokenType.bearer)
    mock_post.assert_called_once_with(
        kc_config.uma2.token_endpoint, data=payload, headers=header
    )


@patch("keycloak.mixins.authorization.requests.post")
@patch("keycloak.mixins.authorization.basic_auth")
def test_introspect(mock_basic_auth, mock_post, kc_client, kc_config):
    rpt = "rpt123456789"
    payload = {"token_type_hint": TokenTypeHints.rpt, "token": rpt}
    token = "token123456789"
    header = {"Authorization": token}
    mock_basic_auth.return_value = header
    kc_client.introspect(rpt)
    mock_basic_auth.assert_called_once_with(
        kc_config.client.client_id, kc_config.client.client_secret
    )
    mock_post.assert_called_once_with(
        kc_config.uma2.introspection_endpoint, data=payload, headers=header
    )


@patch("keycloak.mixins.authorization.requests.get")
@patch("keycloak.mixins.authorization.auth_header")
def test_resources(mock_auth_header, mock_get, kc_client, kc_config):
    token = "token123456789"
    header = {"Authorization": token}
    mock_auth_header.return_value = header
    kc_client.resources(token)
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(
        kc_config.uma2.resource_registration_endpoint, headers=header
    )


@patch("keycloak.mixins.authorization.requests.get")
@patch("keycloak.mixins.authorization.auth_header")
def test_resource(mock_auth_header, mock_get, kc_client, kc_config):
    token = "token123456789"
    resource = "resource123456789"
    header = {"Authorization": token}
    endpoint = f"{kc_config.uma2.resource_registration_endpoint}/{resource}"
    mock_auth_header.return_value = header
    kc_client.resource(resource, token)
    mock_auth_header.assert_called_once_with(token)
    mock_get.assert_called_once_with(endpoint, headers=header)
