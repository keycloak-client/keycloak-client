#! -*- coding: utf-8 -*-
import base64
import json

import jwt
import requests
from jwt.algorithms import (
    ECAlgorithm,
    HMACAlgorithm,
    RSAAlgorithm,
    RSAPSSAlgorithm,
)

from .utils import fix_padding


class JwtMixin(object):
    """ This class consists of methods that can be user to perform JWT operations """

    @property
    def keys(self):
        """
        Method to retrieve keys used to sign jwt tokens

        Returns:
            list
        """
        response = requests.get(self.config['certs_endpoint'])
        response.raise_for_status()
        return response.json().get('keys', [])

    @staticmethod
    def parse_header(jwt_header):
        """
        Method to decode JWT header

        Args:
            jwt_header (str): base64 encoded header segment of the jwt

        Returns:
            dict
        """

        # fix padding
        jwt_header = fix_padding(jwt_header)

        # decode header
        jwt_header = base64.b64decode(jwt_header)

        # convert to dictionary
        return json.loads(jwt_header)

    def get_signing_key(self, jwt_header):
        """
        Method to retrieve signing key

        Args:
            jwt_header (dict): decoded jwt header as dict

        Returns:
            jwt.algorithms.RSAAlgorithm
        """

        # identify key json
        for key in self.keys:
            if key['kid'] == jwt_header['kid']:
                key_json = json.dumps(key)
                break

        # construct public key
        algorithm = jwt_header['alg']

        # see the following git issue to understand why public keys has been built this way
        # https://github.com/jpadilla/pyjwt/issues/359

        # handle EC
        if algorithm in ('ES256', 'ES384', 'ES521', 'ES512'):
            return ECAlgorithm.from_jwk(key_json)

        # handle HMAC
        if algorithm in ('HS256', 'HS384', 'HS512'):
            return HMACAlgorithm.from_jwk(key_json)

        # handle RSA
        if algorithm in ('RS256', 'RS384', 'RS512'):
            return RSAAlgorithm.from_jwk(key_json)

        # handle RSAPSS
        if algorithm in ('PS256', 'PS384', 'PS512'):
            return RSAPSSAlgorithm.from_jwk(key_json)

    @staticmethod
    def get_signing_algorithm(jwt_header):
        """
        Method to retrieve signing algorithm

        Args:
            jwt_header (dict): decoded jwt header as dict
        """
        return jwt_header['alg']

    def decode_jwt(self, token, verify_aud=False, verify_iss=False):
        """
        Method to decode JWT token

        Args:
            token (str): JWT token
            verify_aud (bool): flag to validate audience or not
            verify_iss (bool): flag to validate issuer or not
        """

        # parse jwt segments
        header, payload, signature = token.split('.')

        # parse jwt header
        header = self.parse_header(header)

        # parse signing key and algorithm
        signing_key = self.get_signing_key(header)
        signing_algorithm = self.get_signing_algorithm(header)

        # decrypt jwt
        options = {'verify_aud': verify_aud, 'verify_iss': verify_iss}
        return jwt.decode(token, signing_key, algorithms=[signing_algorithm], options=options)
