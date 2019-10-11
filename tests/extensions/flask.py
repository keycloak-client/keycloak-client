# -*- coding: utf-8 -*-
from unittest.mock import patch


def test_redirect_to_auth(flask_client):
    response = flask_client.get("/")
    assert response.status_code == 302
    assert "/kc/login" in response.headers["Location"]
