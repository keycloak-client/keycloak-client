# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, call, patch

from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from keycloak.constants import GrantTypes
from keycloak.extensions.starlette import AuthenticationMiddleware
from keycloak.utils import auth_header

app = Starlette()
app.add_middleware(
    AuthenticationMiddleware,
    callback_url="http://testserver/kc/callback",
    login_redirect_uri="/howdy",
    logout_redirect_uri="/logout",
)
app.add_middleware(SessionMiddleware, secret_key="key0123456789")


@app.route("/howdy")
async def howdy(request):
    return PlainTextResponse("Howdy!")


@app.route("/logout")
async def logout(request):
    return PlainTextResponse("Logged out!")


def test_no_login():
    """Test case for invalid login"""
    with TestClient(app) as client:
        response = client.get("/howdy", follow_redirects=False)
        assert response.status_code == 307


def test_kc_callback_invalid_state():
    """Test case for callbacks with invalid state"""
    with TestClient(app) as client:
        response = client.get(
            "/kc/callback?state=state123&code=code123", follow_redirects=False
        )
        assert response.status_code == 403
        assert response.content == b"Invalid state"


@patch("keycloak.core.asynchronous.authentication.httpx.AsyncClient.get")
@patch("keycloak.core.asynchronous.authentication.httpx.AsyncClient.post")
@patch("starlette.endpoints.Request")
def test_kc_callback(mock_request, mock_post, mock_get, kc_config):
    mock_request.return_value = MagicMock()
    mock_request.return_value.method = "GET"
    mock_request.return_value.session = {"state": "state123"}
    mock_request.return_value.query_params = {"state": "state123", "code": "code123"}
    mock_request.return_value.url = MagicMock()
    mock_request.return_value.url.path = "/kc/callback"
    mock_post.return_value = MagicMock()
    mock_post.return_value.json.return_value = {
        "access_token": "token12345",
        "refresh_token": "token12345",
    }
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = {}
    payload = {
        "code": "code123",
        "grant_type": GrantTypes.authorization_code,
        "client_id": kc_config.client.client_id,
        "client_secret": kc_config.client.client_secret,
        "redirect_uri": "http://testserver/kc/callback",
    }
    headers = auth_header("token12345")
    token_api_expected_calls = [
        call(kc_config.openid.token_endpoint, data=payload),
        call().raise_for_status(),
        call().json(),
    ]
    userinfo_api_expected_calls = [
        call(kc_config.openid.userinfo_endpoint, headers=headers),
        call().raise_for_status(),
        call().json(),
    ]
    with TestClient(app) as client:
        response = client.get(
            "/kc/callback?state=state123&code=code123", follow_redirects=False
        )
        assert response.status_code == 307
        # mock_post.assert_has_calls(token_api_expected_calls)
        # mock_get.assert_has_calls(userinfo_api_expected_calls)


@patch("keycloak.extensions.starlette.Request")
def test_login_success(mock_request):
    mock_request.return_value = MagicMock()
    mock_request.return_value.method = "GET"
    mock_request.return_value.session = {"user": ""}
    mock_request.return_value.url = MagicMock()
    mock_request.return_value.url.path = "/howdy"
    with TestClient(app) as client:
        response = client.get("/howdy", follow_redirects=False)
        assert response.status_code == 200
        assert response.content == b"Howdy!"
