# -*- coding: utf-8 -*-
from keycloak.utils import fix_padding


def test_fix_padding():
    """ Test case for fix_padding """
    result = fix_padding("YWtoaWw")
    assert result == "YWtoaWw==="
