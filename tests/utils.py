# -*- coding: utf-8 -*-
from keycloak.utils import fix_padding, b64encode, b64decode, basic_auth


def test_fix_padding():
    """ Test case for fix_padding """
    result = fix_padding("YWtoaWw")
    assert result == "YWtoaWw==="


def test_b64encode():
    """ Test case for b64encode """
    result = b64encode("my-data")
    assert result == "bXktZGF0YQ=="


def test_b64decode():
    """ Test case for b64encode """
    result = b64decode("bXktZGF0YQ==")
    assert result == "my-data"


def test_basic_auth():
    """ Test case for basic_auth """
    actual_result = basic_auth("username", "password")
    assert actual_result == {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}
