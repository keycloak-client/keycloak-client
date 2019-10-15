# -*- coding: utf-8 -*-
import base64
import json
import logging
from typing import List, Tuple, Union, Dict

import jwt
import requests
from jwt import algorithms

from ..config import config
from ..constants import Logger, Algorithms
from ..exceptions import AlgorithmNotSupported
from ..utils import fix_padding


log = logging.getLogger(Logger.name)


class JWTMixin:
    """ This class consists of methods that can be user to perform JWT operations """

    _certs: List = []

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
        if alg in Algorithms.ec:
            return algorithms.ECAlgorithm.from_jwk(jwk)
        if alg in Algorithms.hmac:
            return algorithms.HMACAlgorithm.from_jwk(jwk)
        if alg in Algorithms.rsa:
            return algorithms.RSAAlgorithm.from_jwk(jwk)
        if alg in Algorithms.rsapss:
            return algorithms.RSAPSSAlgorithm.from_jwk(jwk)
        raise AlgorithmNotSupported

    def _parse_key_and_alg(self, header: str) -> Tuple[bytes, str]:

        # decode header
        header = fix_padding(header)
        header_decoded = base64.b64decode(header)
        header_as_dict = json.loads(header_decoded)

        # fetch jwk
        kid = header_as_dict.get("kid")
        jwk = self._jwk(kid)

        # fetch key
        alg = header_as_dict.get("alg")
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
