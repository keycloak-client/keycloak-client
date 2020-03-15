# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from typing import List, Tuple, Union, Dict

import jwt
import requests
from jwt import algorithms

from ..config import config
from ..constants import Logger, Algorithms
from ..exceptions import AlgorithmNotSupported
from ..utils import b64decode, basic_auth, handle_exceptions


log = logging.getLogger(Logger.name)


class TokenMixin:
    """ This class consists of methods that can be user to perform JWT operations """

    _jwks: List = []
    _tokens: Dict = {}

    @property
    def tokens(self) -> Dict:
        """
        access and refresh tokens associated with the client/user

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.tokens
        >>>

        :returns: dictionary
        """
        if not self._tokens:
            self._tokens = self.pat(self.username, self.password)  # type: ignore
        return self._tokens

    @tokens.setter
    def tokens(self, val: Dict) -> None:
        """ setter for tokens """
        self._tokens = val

    @property
    def access_token(self) -> str:
        """
        access token associated with the client/user

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.access_token
        >>>

        :returns: string
        """
        return self.tokens["access_token"]

    @property
    def refresh_token(self) -> str:
        """
        refresh token associated with the client/user

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.refresh_token
        >>>

        :returns: string
        """
        return self.tokens["refresh_token"]

    @property
    def scope(self) -> str:
        """
        scopes available

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.scope
        >>>

        :returns: list
        """
        return self.tokens["scope"].split(" ")

    @property
    def token_type(self) -> str:
        """
        type of token

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.token_type
        >>>

        :returns: string
        """
        return self.tokens["token_type"]

    @handle_exceptions
    def refresh_tokens(self) -> None:
        """
        method to refresh expired access token using refresh token

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.refresh_tokens()
        >>>
        """
        headers = basic_auth(config.client.client_id, config.client.client_secret)
        payload = {
            "client_id": config.client.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self._tokens["refresh_token"],
        }
        log.debug("Refreshing tokens")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("Tokens refreshed successfully")
        self._tokens = response.json()

    @handle_exceptions
    def load_jwks(self) -> List:
        """
        retrieve signing keys/JWK from the keycloak server

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.load_jwks()
        >>>

        :returns: list
        """
        log.debug("Retrieving JWKs from keycloak server")
        response = requests.get(config.uma2.jwks_uri)
        response.raise_for_status()
        log.debug("JWKs retrieved successfully")
        return response.json().get("keys", [])

    @property
    def jwks(self) -> List:
        """
        list of signing keys/JWKs used by the keycloak server

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.jwks
        >>>

        :returns: list
        """
        if not self._jwks:
            self._jwks = self.load_jwks()
        return self._jwks

    def find_jwk(self, kid: str) -> str:
        """
        find jwk with given id from self.jwks

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.find_jwk()
        >>>

        :returns: string
        """
        for item in self.jwks:
            if item["kid"] == kid:
                break
        return json.dumps(item)

    @staticmethod
    def construct_key(alg: str, jwk: str) -> bytes:
        if alg in Algorithms.ec:
            return algorithms.ECAlgorithm.from_jwk(jwk)  # pragma: nocover
        if alg in Algorithms.hmac:
            return algorithms.HMACAlgorithm.from_jwk(jwk)  # pragma: nocover
        if alg in Algorithms.rsapss:
            return algorithms.RSAPSSAlgorithm.from_jwk(jwk)  # pragma: nocover
        if alg in Algorithms.rsa:
            return algorithms.RSAAlgorithm.from_jwk(jwk)
        raise AlgorithmNotSupported

    def parse_key_and_alg(self, header: str) -> Tuple[bytes, str]:
        """ retrieve signing key and algorithm from given jwt header """
        decoded_header: Dict = b64decode(header, deserialize=True)  # type: ignore
        kid = decoded_header["kid"]
        jwk = self.find_jwk(kid)
        alg = decoded_header["alg"]
        key = self.construct_key(alg, jwk)
        return key, alg

    def decode(self, token: str) -> Dict:
        """ decode given json web token (jwt) """
        header, body, signature = token.split(".")
        key, algorithm = self.parse_key_and_alg(header)
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            issuer=config.uma2.issuer,
            audience=config.client.client_id,
        )
