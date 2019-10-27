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

    _certs: List = []
    _tokens: Dict = {}
    _issued_at: datetime = datetime.utcnow()

    @property
    def tokens(self) -> Dict:
        """ getter for tokens """

        # handle empty tokens
        if self._tokens == {}:
            self._issued_at = datetime.utcnow()
            self._tokens = self.pat(self.username, self.password)  # type: ignore

        # handle expired tokens
        if self.expired:
            self._issued_at = datetime.utcnow()
            self._tokens = self._renew()

        # return tokens
        return self._tokens

    @tokens.setter
    def tokens(self, val: Dict) -> None:
        self._tokens = val

    @property
    def access_token(self) -> str:
        return self.tokens["access_token"]

    @property
    def expires_in(self) -> int:
        val = self._tokens["expires_in"]
        return int(val)

    @property
    def now(self) -> datetime:
        return datetime.utcnow()

    @property
    def age(self) -> int:
        val = self.now - self._issued_at
        return val.seconds

    @property
    def expired(self) -> bool:
        return self.age >= self.expires_in

    def _renew(self) -> Dict:
        """ method to renew tokens """

        # prepare headers
        headers = basic_auth(config.client.client_id, config.client.client_secret)

        # prepare payload
        payload = {
            "client_id": config.client.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self._tokens["refresh_token"],
        }

        # renew tokens
        log.info("Renewing tokens")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            log.exception("Failed to renew tokens\n %s", response.content)
            raise ex

        # return tokens
        return response.json()

    def load_keys(self) -> None:
        log.info("Retrieving keys from keycloak server")
        response = requests.get(config.uma2.jwks_uri)
        response.raise_for_status()
        self._certs = response.json().get("keys", [])

    @property
    def _keys(self) -> List:
        if not self._certs:
            self.load_keys()
        return self._certs

    def _jwk(self, kid: str) -> str:
        key: Dict = {}
        for item in self._keys:
            if item["kid"] == kid:
                key = item
        return json.dumps(key)

    @staticmethod
    def _key(alg: str, jwk: str) -> bytes:
        # fmt: off
        if alg in Algorithms.ec:
            return algorithms.ECAlgorithm.from_jwk(jwk)      # pragma: nocover
        if alg in Algorithms.hmac:
            return algorithms.HMACAlgorithm.from_jwk(jwk)    # pragma: nocover
        if alg in Algorithms.rsapss:
            return algorithms.RSAPSSAlgorithm.from_jwk(jwk)  # pragma: nocover
        # fmt: on
        if alg in Algorithms.rsa:
            return algorithms.RSAAlgorithm.from_jwk(jwk)
        raise AlgorithmNotSupported

    def _parse_key_and_alg(self, header: str) -> Tuple[bytes, str]:

        # decode header
        decoded_header: Dict = b64decode(header, deserialize=True)  # type: ignore

        # fetch jwk
        kid = decoded_header["kid"]
        jwk = self._jwk(kid)

        # fetch key
        alg = decoded_header["alg"]
        key = self._key(alg, jwk)

        return key, alg

    def decode(self, token: str) -> Dict:
        header, _, _ = token.split(".")
        key, algorithm = self._parse_key_and_alg(header)
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            issuer=config.uma2.issuer,
            audience=config.client.client_id,
        )
