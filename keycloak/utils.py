#! -*- coding: utf-8 -*-
import json
import base64


def fix_padding(encoded_string):
    """
    Method to correct padding for base64 encoding

    Args:
        encoded_string (str): base64 encoded string/data

    Returns:
        str
    """

    # calculate padding
    required_padding = len(encoded_string) % 4

    # pad data
    return encoded_string + ('=' * required_padding)


def decode_jwt(jwt_token):
    """
    Method to decode the given jwt token

    Args:
         jwt_token (str): token to be decoded
    """

    # parse token segments
    header, payload, signature = jwt_token.split('.')

    # fix padding
    payload = fix_padding(payload)

    # decode base64 encoded string
    payload = base64.b64decode(payload)

    # convert json to dict
    return json.loads(payload)
