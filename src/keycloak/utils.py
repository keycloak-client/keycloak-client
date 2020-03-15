# -*- coding: utf-8 -*-
import base64
import json
import logging
from typing import Tuple, Dict, Union, Any, Callable
from functools import wraps

from requests.exceptions import HTTPError

from .constants import Headers, TokenType, Logger


log = logging.getLogger(Logger.name)


def b64encode(data: Any, serialize: bool = False) -> str:
    """ method to encode string using base64 """
    serialized_data = json.dumps(data) if serialize else data
    data_as_bytes = serialized_data.encode("utf-8")
    return base64.b64encode(data_as_bytes).decode("utf-8")


def b64decode(string: str, deserialize: bool = False) -> Union[str, Dict]:
    """ method to decode string using base64 """
    string = fix_padding(string)
    decoded_string = base64.b64decode(string).decode("utf-8")
    return json.loads(decoded_string) if deserialize else decoded_string


def auth_header(token_val: str, token_type: str = TokenType.bearer) -> Dict:
    """ method to generate authorization header """
    return {Headers.authorization: f"{token_type} {token_val}"}


def basic_auth(username: str, password: str) -> Dict:
    """ method to prepare the basic auth header """
    token = f"{username}:{password}"
    token = b64encode(token)
    return auth_header(token, TokenType.basic)


def fix_padding(encoded_string: str) -> str:
    """ method to correct padding for base64 encoding """
    required_padding = len(encoded_string) % 4
    return encoded_string + ("=" * required_padding)


def handle_exceptions(func: Callable) -> Any:
    """ decorator to take care of HTTPError """

    @wraps(func)
    def wrapper(*args: Tuple, **kwargs: Dict) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPError as ex:
            if hasattr(ex.response, "content"):
                log.exception(ex.response.content)
            raise ex
        except Exception as ex:
            log.exception("Error occurred:")
            raise ex

    return wrapper


class Singleton(type):
    """ metaclass for creating singleton classes """

    _instances: Dict = {}

    def __call__(cls, *args: Tuple, **kwargs: Dict) -> type:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
