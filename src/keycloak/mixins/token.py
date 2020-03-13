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
from ..utils import b64decode, basic_auth


log = logging.getLogger(Logger.name)


class TokenMixin:
    """ This class consists of methods that can be user to perform JWT operations """

    _jwks: List = []
    _tokens: Dict = {}

    @property
    def tokens(self) -> Dict:
        """ getter for tokens """

        # retrieve tokens if not available
        if not self._tokens:
            self._tokens = self.pat(self.username, self.password)  # type: ignore

        return self._tokens

    @tokens.setter
    def tokens(self, val: Dict) -> None:
        """ setter for tokens """
        self._tokens = val

    @property
    def access_token(self) -> str:
        return self.tokens["access_token"]

    @property
    def refresh_token(self) -> str:
        return self.tokens["refresh_token"]

    def refresh_access_token(self) -> Dict:
        """ refresh access token using the refresh token """

        # prepare headers
        headers = basic_auth(config.client.client_id, config.client.client_secret)

        # prepare payload
        payload = {
            "client_id": config.client.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self._tokens["refresh_token"],
        }

        # refresh access token
        log.info("Refreshing access token")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception("Failed to refresh access token\n %s", response.content)
            raise ex

        return response.json()

    def load_jwks(self) -> List:
        log.info("Retrieving JWT signing keys from keycloak server")
        response = requests.get(config.uma2.jwks_uri)
        response.raise_for_status()
        return response.json().get("keys", [])

    @property
    def jwks(self) -> List:
        if not self._jwks:
            self._jwks = self.load_jwks()
        return self._jwks

    def find_jwk(self, kid: str) -> str:
        """ find jwk with given id from self.jwks """
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

        # decode header
        decoded_header: Dict = b64decode(header, deserialize=True)  # type: ignore

        # find jwk
        kid = decoded_header["kid"]
        jwk = self.find_jwk(kid)

        # construct key from jwk
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
