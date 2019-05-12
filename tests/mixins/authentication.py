#! -*- coding: utf-8 -*-
import urllib
from unittest.mock import MagicMock, patch


@patch("keycloak.mixins.authentication.uuid.uuid4")
def test_authentication_url(mock_uuid4, keycloak_client):
    """ Test case for authentication_url """
    mock_uuid4.return_value = "862e94e4-e04b-463b-8d08-577161684b76"
    arguments = urllib.parse.urlencode(
        {
            "state": "862e94e4-e04b-463b-8d08-577161684b76",
            "client_id": keycloak_client.config.client_id,
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": keycloak_client.config.redirect_uri,
        }
    )
    authentication_url = keycloak_client.config.authorization_endpoint + "?" + arguments
    _authentication_url, _ = keycloak_client.authentication_url()
    assert authentication_url is not None
    assert authentication_url == _authentication_url


@patch("keycloak.mixins.authentication.requests.post")
def test_authentication_callback(mock_post, keycloak_client):
    """ Test case for authentication_callback """
    mock_post.return_value.json = MagicMock()
    payload = {
        "code": "code123456789",
        "grant_type": "authorization_code",
        "client_id": keycloak_client.config.client_id,
        "redirect_uri": keycloak_client.config.redirect_uri,
        "client_secret": keycloak_client.config.client_secret,
    }
    keycloak_client.authentication_callback(code="code123456789")
    mock_post.assert_called_once_with(
        keycloak_client.config.token_endpoint, data=payload
    )
    mock_post.return_value.json.assert_called_once()
