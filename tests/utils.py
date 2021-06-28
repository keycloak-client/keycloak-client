# -*- coding: utf-8 -*-
from keycloak.utils import b64encode, basic_auth, fix_padding


def test_fix_padding():
    """Test case for fix_padding"""
    result = fix_padding("YWtoaWw")
    assert result == "YWtoaWw==="


def test_b64encode():
    """Test case for b64encode"""
    result = b64encode("my-data")
    assert result == "bXktZGF0YQ=="


def test_basic_auth():
    """Test case for basic_auth"""
    actual_result = basic_auth("username", "password")
    assert actual_result == {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}
