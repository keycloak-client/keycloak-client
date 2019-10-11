# -*- coding: utf-8 -*-
import base64
from typing import Dict

from .constants import Headers, TokenType


def b64encode(string: str) -> str:
    """ method to encode string using base64 """
    string = bytes(string, "utf-8")
    string = base64.b64encode(string)
    return string.decode("utf-8")


def auth_header(token_val: str, token_type: str = TokenType.bearer) -> Dict:
    """ method to generate authorization header """
    return {Headers.authorization: f"{token_type} {token_val}"}


def basic_auth(username, password) -> Dict:
    """ method to prepare the basic auth header """
    token = f"{username}:{password}"
    token = b64encode(token)
    return auth_header(token, TokenType.basic)


def fix_padding(encoded_string: str) -> str:
    """ method to correct padding for base64 encoding """
    required_padding = len(encoded_string) % 4
    return encoded_string + ("=" * required_padding)


class Singleton(type):
    """ metaclass for creating singleton classes """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
