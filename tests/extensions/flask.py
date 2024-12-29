# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, PropertyMock, call, patch

from flask import Flask

from keycloak.constants import GrantTypes
from keycloak.extensions.flask import AuthenticationMiddleware
from keycloak.utils import auth_header


def get_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret0123456789"
    app.wsgi_app = AuthenticationMiddleware(
        app.wsgi_app,
        app.config,
        app.session_interface,
        callback_url="http://testserver/kc/callback",
        login_redirect_uri="/howdy",
        logout_redirect_uri="/logout",
    )

    @app.route("/howdy")
    def howdy():
        return "Howdy!"

    @app.route("/logout")
    def logout():
        return "Logged out!"

    return app


def test_login():
    app = get_app()
    client = app.test_client()
    response = client.get("/howdy")
    assert response.status_code == 302
    assert "https://keycloak-server.com/" in response.headers["Location"]


@patch("keycloak.core.authentication.httpx.get")
@patch("keycloak.core.authentication.httpx.post")
@patch("keycloak.core.authentication.uuid4")
@patch.object(AuthenticationMiddleware, "session_interface", new_callable=PropertyMock)
def test_callback(mock_session_interface, mock_uuid4, mock_post, mock_get, kc_config):
    mock_session_interface.return_value = MagicMock()
    mock_session_interface.return_value.open_session.return_value = {
        "state": "state123"
    }
    mock_uuid4.return_value = MagicMock()
    mock_uuid4.return_value.hex.return_value = "0123456789"
    mock_post.return_value = MagicMock()
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = {"name": "123"}
    token_endpoint_payload = {
        "code": "code123",
        "grant_type": GrantTypes.authorization_code,
        "redirect_uri": "http://localhost/kc/callback",
        "client_id": kc_config.client.client_id,
        "client_secret": kc_config.client.client_secret,
    }
    userinfo_endpoint_header = auth_header("token123")
    token_api_expected_calls = [
        call(kc_config.openid.token_endpoint, data=token_endpoint_payload),
        call().raise_for_status(),
        call().json(),
    ]
    userinfo_api_expected_calls = [
        call(kc_config.openid.userinfo_endpoint, headers=userinfo_endpoint_header),
        call().raise_for_status(),
        call().json(),
    ]
    app = get_app()
    client = app.test_client()
    response = client.get("http://testserver/kc/callback?state=state123&code=code123")
    assert response.status_code == 302
    mock_post.assert_has_calls(token_api_expected_calls)
    mock_get.assert_has_calls(userinfo_api_expected_calls)


@patch.object(AuthenticationMiddleware, "session_interface", new_callable=PropertyMock)
def test_invalid_callback(mock_session_interface):
    mock_session_interface.return_value = MagicMock()
    mock_session_interface.return_value.open_session.return_value = {"state": "unknown"}
    app = get_app()
    client = app.test_client()
    response = client.get("http://testserver/kc/callback?state=state123&code=code123")
    assert response.status_code == 403
    assert response.data == b"Invalid state"


@patch.object(AuthenticationMiddleware, "session_interface", new_callable=PropertyMock)
def test_valid_request(mock_session_interface):
    mock_session_interface.return_value = MagicMock()
    mock_session_interface.return_value.open_session.return_value = {
        "user": "user-data"
    }
    app = get_app()
    client = app.test_client()
    response = client.get("/howdy")
    assert response.status_code == 200
    assert response.data == b"Howdy!"
