#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with json web tokens """

import base64
import json

import jwt
import requests
from cached_property import cached_property_with_ttl

from ..utils import fix_padding


class JwtMixin:
    """ This class consists of methods that can be user to perform JWT operations """

    @cached_property_with_ttl(ttl=86400)
    def keys(self):
        """
        Method to retrieve keys used to sign jwt tokens

        Returns:
            list
        """
        response = requests.get(self.config.jwks_uri)
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

    def get_key_json(self, kid):
        """
        Method to retrieve key using kid

        Args:
            kid (str): unique key identifier

        Returns:
            str
        """
        _key = {}
        for key in self.keys:
            if key['kid'] == kid:
                _key = key
        return json.dumps(_key)

    # pylint: disable=inconsistent-return-statements
    def get_signing_key(self, jwt_header):
        """
        Method to retrieve signing key

        Args:
            jwt_header (dict): decoded jwt header as dict

        Returns:
            jwt.algorithms.Algorithm
        """

        # parse jwt header info
        kid = jwt_header.get('kid')
        alg = jwt_header.get('alg')

        # fetch public key
        key_json = self.get_key_json(kid)

        # see the following git issue to understand why public keys has been built this way
        # https://github.com/jpadilla/pyjwt/issues/359

        # handle EC
        if alg in ('ES256', 'ES384', 'ES521', 'ES512'):
            return jwt.algorithms.ECAlgorithm.from_jwk(key_json)

        # handle HMAC
        if alg in ('HS256', 'HS384', 'HS512'):
            return jwt.algorithms.HMACAlgorithm.from_jwk(key_json)

        # handle RSA
        if alg in ('RS256', 'RS384', 'RS512'):
            return jwt.algorithms.RSAAlgorithm.from_jwk(key_json)

        # handle RSAPSS
        if alg in ('PS256', 'PS384', 'PS512'):
            return jwt.algorithms.RSAPSSAlgorithm.from_jwk(key_json)

    @staticmethod
    def get_signing_algorithm(jwt_header):
        """
        Method to retrieve signing algorithm

        Args:
            jwt_header (dict): decoded jwt header as dict
        """
        return jwt_header.get('alg')

    def decode_jwt(self, token, verify_aud=False, verify_iss=False):
        """
        Method to decode JWT token

        Args:
            token (str): JWT token
            verify_aud (bool): flag to validate audience or not
            verify_iss (bool): flag to validate issuer or not
        """

        # parse jwt segments
        header, _, _ = token.split('.')

        # parse jwt header
        header = self.parse_header(header)

        # parse signing key and algorithm
        signing_key = self.get_signing_key(header)
        signing_algorithm = self.get_signing_algorithm(header)

        # decrypt jwt
        options = {'verify_aud': verify_aud, 'verify_iss': verify_iss}
        return jwt.decode(token, signing_key, algorithms=[signing_algorithm], options=options)

    def refresh_access_token(self, refresh_token):
        """
        Method to refresh access token using refresh token

        Args:
            refresh_token (str): refresh token using which new access_token can be retrieved
        """

        # prepare payload
        payload = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        # send request to keycloak server
        response = requests.post(self.config.token_endpoint, data=payload)
        response.raise_for_status()

        return response.json()
