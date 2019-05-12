#! -*- coding: utf-8 -*-

""" utility functions """

import base64


def b64encode(string):
    """
    Method to encode string using base64

    Args:
        string (str): data to be encoded

    Returns:
        str
    """
    # convert to bytes
    string = bytes(string, "utf-8")

    # perform base64 encoding
    string = base64.b64encode(string)

    # convert to str
    return string.decode("utf-8")


def auth_header(token_val, token_type):
    """
    Method to generate authorization header to be used with the requests

    Args:
        token_val (str): authentication token
        token_type (str): token type eg: Basic, Bearer etc

    Returns:
        dict
    """
    return {"Authorization": "{} {}".format(token_type, token_val)}


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
    return encoded_string + ("=" * required_padding)
