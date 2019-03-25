#! -*- coding: utf-8 -*-


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
