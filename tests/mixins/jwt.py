# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

import pytest


@patch("keycloak.mixins.jwt.requests.get")
def test_keys(mock_get, kc_client, kc_config, monkeypatch):
    """ Test case for keys """
    monkeypatch.setattr(kc_client, "_certs", [])
    mock_get.return_value.json = MagicMock()
    kc_client._keys
    mock_get.assert_called_once_with(kc_config.uma2.jwks_uri)
    mock_get.return_value.json.assert_called_once()


def test_jwk(kc_client):
    key = kc_client._jwk("jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q")
    assert key == json.dumps(
        {
            "kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "gvG6nS5gWCU60KbcjoMScEyo_avU0I1gfnKp-wNzL5n1MU3AexLp4dErafyXhwuHDc1Kx-v76NGykjpgMXTknhxltxJI9wewn6nDSSF6g-Qz08dUCstl3kdkwOXBYPqmbXknSMGTgQ4X94kFR4QeUUf_qdJxKaqB2eGciX5XGb95Z5rPFjH41wgyj_VcuZVfzSKj915PbJAMXEjGUtN-PNfEvF_3SPvRGU3lv-agAGlJrhBdNsnuVmnobgwufYC8XNwK3jkgprBWoH5UU3gUUH0979e8hYAov3wKlRT4X2HQDNrQvlne7ysAIIMp5XmrOctTcmT1AIPe8k0-41s0Xw",
            "e": "AQAB",
        }
    )


@pytest.mark.skip()
@patch("keycloak.mixins.jwt.base64.b64decode")
@patch("keycloak.mixins.jwt.fix_padding")
def test_parse_key_and_alg(mock_fix_padding, mock_b64decode, kc_client):
    """ Test case for parse_header """
    header_encoded = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqVmFzcjZPR0w1azBWRkJzdWJLdWMzWGdlYWMtQWZwcW9YVkdrbUFhbjRRIn0"
    header_decoded = '{"kid": "jVasr6OGL5k0VFBsubKuc3Xgeac-AfpqoXVGkmAan4Q", "alg": "RS256", "typ": "JWT"}'
    mock_fix_padding.return_value = header_encoded
    mock_b64decode.return_value = header_decoded
    kc_client._parse_key_and_alg(header_encoded)
    mock_fix_padding.assert_called_once_with(header_encoded)
    mock_b64decode.assert_called_once_with(header_encoded)


@patch("keycloak.mixins.jwt.jwt.decode")
@patch("keycloak.mixins.jwt.JWTMixin._parse_key_and_alg")
def test_decode(mock_parse_key_and_alg, mock_decode, kc_client, kc_config):
    """ Test case for decode_jwt """
    token = "header.payload.signature"
    mock_parse_key_and_alg.return_value = ("key", "algorithm")
    kc_client.decode(token)
    mock_parse_key_and_alg.assert_called_once_with("header")
    mock_decode.assert_called_once_with(
        token,
        "key",
        algorithms=["algorithm"],
        issuer=kc_config.uma2.issuer,
        audience=kc_config.client.client_id,
    )
