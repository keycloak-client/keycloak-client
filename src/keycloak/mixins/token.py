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
        {'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJLRG9qblhUaF90Z0dzeWtDM1g4VjJfaEY3TU0zZlZpa1B6T2VDX2RiLWx3In0.eyJqdGkiOiIzOWJkMDQ0ZS04OGQ3LTQ3MGQtOGE4Ni1hMWMxMWI2ZmI2MzIiLCJleHAiOjE1ODQyNTcwMjgsIm5iZiI6MCwiaWF0IjoxNTg0MjU2OTY4LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbImtleWNsb2FrLWNsaWVudCIsImFjY291bnQiXSwic3ViIjoiNmJhMDg0NDMtMzg4MS00MGU3LWFmNDMtMTBiNzE5NmIwMmZkIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoia2V5Y2xvYWstY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiNWU3ZDcyMjUtMGVjNi00NTgxLWE3OWEtMDkyMWI2ZjYzMDFhIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsia2V5Y2xvYWstY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImNsaWVudElkIjoia2V5Y2xvYWstY2xpZW50IiwiY2xpZW50SG9zdCI6IjE3Mi4xNy4wLjEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQta2V5Y2xvYWstY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xNy4wLjEifQ.Yx_GlS3VUl9SfqH185A1G-ZKnTLdPVkRaLoNlXZYG-yA3g85293T4cRayqWDy-aSs0QrhcFht4E-x0PfXZXkS-F_mdByJXzkojCtS3zwztCvUt1667RTc-tRqxqiU3jzdrQw8pQSPKJBBwwrVOthoowc17uSCr7QmvNf2VUA6411ySyzrqr2Hm5Y8oUpcY-eAeN3ivxuIHfCIyv2QRj4MchthY8mZkZGltJygZIN3fHSqiNmgv29NGQDZQ7JMDRg1dKDqFVEmmhObtmjiYu1jpxX3Z3rLGw3AfpdzkfLlC7Bd0qNjLIYQDfmniX1-LK9eEzvUGSD3Mf0bHvfgw5qlg', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjYmFkZWRhYS04NDA5LTQ3MDYtODcwMy02NjViM2Q2MzYwMDAifQ.eyJqdGkiOiJkODVhOWJlYi03NzE1LTQ4ZTAtOTA3My00ZDEyMmQ4MDM1NzAiLCJleHAiOjE1ODQyNTg3NjgsIm5iZiI6MCwiaWF0IjoxNTg0MjU2OTY4LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6IjZiYTA4NDQzLTM4ODEtNDBlNy1hZjQzLTEwYjcxOTZiMDJmZCIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJrZXljbG9hay1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiI1ZTdkNzIyNS0wZWM2LTQ1ODEtYTc5YS0wOTIxYjZmNjMwMWEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImtleWNsb2FrLWNsaWVudCI6eyJyb2xlcyI6WyJ1bWFfcHJvdGVjdGlvbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIn0.K22gl2ICSmVh6omZMk7z4DB_Io4tDiWp__Gxxx_W4Nk', 'token_type': 'bearer', 'not-before-policy': 0, 'session_state': '5e7d7225-0ec6-4581-a79a-0921b6f6301a', 'scope': 'email profile'}
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
        'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJLRG9qblhUaF90Z0dzeWtDM1g4VjJfaEY3TU0zZlZpa1B6T2VDX2RiLWx3In0.eyJqdGkiOiIzOWJkMDQ0ZS04OGQ3LTQ3MGQtOGE4Ni1hMWMxMWI2ZmI2MzIiLCJleHAiOjE1ODQyNTcwMjgsIm5iZiI6MCwiaWF0IjoxNTg0MjU2OTY4LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbImtleWNsb2FrLWNsaWVudCIsImFjY291bnQiXSwic3ViIjoiNmJhMDg0NDMtMzg4MS00MGU3LWFmNDMtMTBiNzE5NmIwMmZkIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoia2V5Y2xvYWstY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiNWU3ZDcyMjUtMGVjNi00NTgxLWE3OWEtMDkyMWI2ZjYzMDFhIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsia2V5Y2xvYWstY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImNsaWVudElkIjoia2V5Y2xvYWstY2xpZW50IiwiY2xpZW50SG9zdCI6IjE3Mi4xNy4wLjEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQta2V5Y2xvYWstY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xNy4wLjEifQ.Yx_GlS3VUl9SfqH185A1G-ZKnTLdPVkRaLoNlXZYG-yA3g85293T4cRayqWDy-aSs0QrhcFht4E-x0PfXZXkS-F_mdByJXzkojCtS3zwztCvUt1667RTc-tRqxqiU3jzdrQw8pQSPKJBBwwrVOthoowc17uSCr7QmvNf2VUA6411ySyzrqr2Hm5Y8oUpcY-eAeN3ivxuIHfCIyv2QRj4MchthY8mZkZGltJygZIN3fHSqiNmgv29NGQDZQ7JMDRg1dKDqFVEmmhObtmjiYu1jpxX3Z3rLGw3AfpdzkfLlC7Bd0qNjLIYQDfmniX1-LK9eEzvUGSD3Mf0bHvfgw5qlg'
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
        'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjYmFkZWRhYS04NDA5LTQ3MDYtODcwMy02NjViM2Q2MzYwMDAifQ.eyJqdGkiOiJkODVhOWJlYi03NzE1LTQ4ZTAtOTA3My00ZDEyMmQ4MDM1NzAiLCJleHAiOjE1ODQyNTg3NjgsIm5iZiI6MCwiaWF0IjoxNTg0MjU2OTY4LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6IjZiYTA4NDQzLTM4ODEtNDBlNy1hZjQzLTEwYjcxOTZiMDJmZCIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJrZXljbG9hay1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiI1ZTdkNzIyNS0wZWM2LTQ1ODEtYTc5YS0wOTIxYjZmNjMwMWEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImtleWNsb2FrLWNsaWVudCI6eyJyb2xlcyI6WyJ1bWFfcHJvdGVjdGlvbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIn0.K22gl2ICSmVh6omZMk7z4DB_Io4tDiWp__Gxxx_W4Nk'
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
        ['email', 'profile']
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
        'bearer'
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
        [{'kid': 'KDojnXTh_tgGsykC3X8V2_hF7MM3fVikPzOeC_db-lw', 'kty': 'RSA', 'alg': 'RS256', 'use': 'sig', 'n': 'q8JxMYdetQKGZHhH6ZzQvnc0S6qfBlUchwuNITAD2_nBlta970_2zE840bxbwQSiZVfMh1fdnQ4xZiIc5qTjeLIn2n6LBs78uzTdAP4PG1tyV2jJviBnJY6FNEHwWKJ-bPLMp_WRze5uSnzwW9sq2e9XhhQY1os9m6tou01GIo93KUnYY94Xvl1MMNjxFAX7RA5MYi-qPw6BNi-b_5WB1LD3A2e-aJUnh40NMwJAPC286Is8KvJIgeg3CMIKPfvVcwzMDUvrLZHRHhvypjvW5ws7OgnNkngCdnz8hyMe4qGNkKl8rbWiu5UOI6qlG3ub4r_CTv6nvqIOdlyO_y97wQ', 'e': 'AQAB', 'x5c': ['MIICmzCCAYMCBgFw3RFEWTANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjAwMzE1MDcxOTIxWhcNMzAwMzE1MDcyMTAxWjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCrwnExh161AoZkeEfpnNC+dzRLqp8GVRyHC40hMAPb+cGW1r3vT/bMTzjRvFvBBKJlV8yHV92dDjFmIhzmpON4sifafosGzvy7NN0A/g8bW3JXaMm+IGcljoU0QfBYon5s8syn9ZHN7m5KfPBb2yrZ71eGFBjWiz2bq2i7TUYij3cpSdhj3he+XUww2PEUBftEDkxiL6o/DoE2L5v/lYHUsPcDZ75olSeHjQ0zAkA8Lbzoizwq8kiB6DcIwgo9+9VzDMwNS+stkdEeG/KmO9bnCzs6Cc2SeAJ2fPyHIx7ioY2QqXyttaK7lQ4jqqUbe5viv8JO/qe+og52XI7/L3vBAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAEIkR4iXNmFWJTyP5j682i7MWeHnMCTMQTQZtOfqbVAJLKMRxm9X8ND/PwbucoLFsmx9UnyCe9erIJ/EGRimTNGij311kRWVtDCw6FtObMaxNvgOLwiuN989N7bA2B6QqsBqYvlYnEHy5rPLJWRojUPQ942mildqRiFI5JfGHjY88gwju/q/DhhAPu7wFORYDYxo0Fxv4/aV/VJzg03gav0/vZWebqEa/aRFSpScZgYxc4KloNMkYZYHYo/OtAX01WUBO5cilbennNnUDeryy3FBc9p1/rv1a1BL9rY5wW2Kt4jYyp82lk+gZqtfHJDHHk44QLW7xq37AYd8JdQMjss='], 'x5t': 'eDziHrpDesOJXALdEuBF2tY4vWc', 'x5t#S256': '__cmdM6AqteNxXRMH4daJGEsG15jZCsSxKTCwYk-PX4'}]
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
        [{'kid': 'KDojnXTh_tgGsykC3X8V2_hF7MM3fVikPzOeC_db-lw', 'kty': 'RSA', 'alg': 'RS256', 'use': 'sig', 'n': 'q8JxMYdetQKGZHhH6ZzQvnc0S6qfBlUchwuNITAD2_nBlta970_2zE840bxbwQSiZVfMh1fdnQ4xZiIc5qTjeLIn2n6LBs78uzTdAP4PG1tyV2jJviBnJY6FNEHwWKJ-bPLMp_WRze5uSnzwW9sq2e9XhhQY1os9m6tou01GIo93KUnYY94Xvl1MMNjxFAX7RA5MYi-qPw6BNi-b_5WB1LD3A2e-aJUnh40NMwJAPC286Is8KvJIgeg3CMIKPfvVcwzMDUvrLZHRHhvypjvW5ws7OgnNkngCdnz8hyMe4qGNkKl8rbWiu5UOI6qlG3ub4r_CTv6nvqIOdlyO_y97wQ', 'e': 'AQAB', 'x5c': ['MIICmzCCAYMCBgFw3RFEWTANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjAwMzE1MDcxOTIxWhcNMzAwMzE1MDcyMTAxWjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCrwnExh161AoZkeEfpnNC+dzRLqp8GVRyHC40hMAPb+cGW1r3vT/bMTzjRvFvBBKJlV8yHV92dDjFmIhzmpON4sifafosGzvy7NN0A/g8bW3JXaMm+IGcljoU0QfBYon5s8syn9ZHN7m5KfPBb2yrZ71eGFBjWiz2bq2i7TUYij3cpSdhj3he+XUww2PEUBftEDkxiL6o/DoE2L5v/lYHUsPcDZ75olSeHjQ0zAkA8Lbzoizwq8kiB6DcIwgo9+9VzDMwNS+stkdEeG/KmO9bnCzs6Cc2SeAJ2fPyHIx7ioY2QqXyttaK7lQ4jqqUbe5viv8JO/qe+og52XI7/L3vBAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAEIkR4iXNmFWJTyP5j682i7MWeHnMCTMQTQZtOfqbVAJLKMRxm9X8ND/PwbucoLFsmx9UnyCe9erIJ/EGRimTNGij311kRWVtDCw6FtObMaxNvgOLwiuN989N7bA2B6QqsBqYvlYnEHy5rPLJWRojUPQ942mildqRiFI5JfGHjY88gwju/q/DhhAPu7wFORYDYxo0Fxv4/aV/VJzg03gav0/vZWebqEa/aRFSpScZgYxc4KloNMkYZYHYo/OtAX01WUBO5cilbennNnUDeryy3FBc9p1/rv1a1BL9rY5wW2Kt4jYyp82lk+gZqtfHJDHHk44QLW7xq37AYd8JdQMjss='], 'x5t': 'eDziHrpDesOJXALdEuBF2tY4vWc', 'x5t#S256': '__cmdM6AqteNxXRMH4daJGEsG15jZCsSxKTCwYk-PX4'}]
        >>>

        :returns: list
        """
        if not self._jwks:
            self._jwks = self.load_jwks()
        return self._jwks

    def fetch_jwk(self, kid: str) -> str:
        """
        find jwk with given id from self.jwks

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.fetch_jwk('KDojnXTh_tgGsykC3X8V2_hF7MM3fVikPzOeC_db-lw')
        '{"kid": "KDojnXTh_tgGsykC3X8V2_hF7MM3fVikPzOeC_db-lw", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "q8JxMYdetQKGZHhH6ZzQvnc0S6qfBlUchwuNITAD2_nBlta970_2zE840bxbwQSiZVfMh1fdnQ4xZiIc5qTjeLIn2n6LBs78uzTdAP4PG1tyV2jJviBnJY6FNEHwWKJ-bPLMp_WRze5uSnzwW9sq2e9XhhQY1os9m6tou01GIo93KUnYY94Xvl1MMNjxFAX7RA5MYi-qPw6BNi-b_5WB1LD3A2e-aJUnh40NMwJAPC286Is8KvJIgeg3CMIKPfvVcwzMDUvrLZHRHhvypjvW5ws7OgnNkngCdnz8hyMe4qGNkKl8rbWiu5UOI6qlG3ub4r_CTv6nvqIOdlyO_y97wQ", "e": "AQAB", "x5c": ["MIICmzCCAYMCBgFw3RFEWTANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjAwMzE1MDcxOTIxWhcNMzAwMzE1MDcyMTAxWjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCrwnExh161AoZkeEfpnNC+dzRLqp8GVRyHC40hMAPb+cGW1r3vT/bMTzjRvFvBBKJlV8yHV92dDjFmIhzmpON4sifafosGzvy7NN0A/g8bW3JXaMm+IGcljoU0QfBYon5s8syn9ZHN7m5KfPBb2yrZ71eGFBjWiz2bq2i7TUYij3cpSdhj3he+XUww2PEUBftEDkxiL6o/DoE2L5v/lYHUsPcDZ75olSeHjQ0zAkA8Lbzoizwq8kiB6DcIwgo9+9VzDMwNS+stkdEeG/KmO9bnCzs6Cc2SeAJ2fPyHIx7ioY2QqXyttaK7lQ4jqqUbe5viv8JO/qe+og52XI7/L3vBAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAEIkR4iXNmFWJTyP5j682i7MWeHnMCTMQTQZtOfqbVAJLKMRxm9X8ND/PwbucoLFsmx9UnyCe9erIJ/EGRimTNGij311kRWVtDCw6FtObMaxNvgOLwiuN989N7bA2B6QqsBqYvlYnEHy5rPLJWRojUPQ942mildqRiFI5JfGHjY88gwju/q/DhhAPu7wFORYDYxo0Fxv4/aV/VJzg03gav0/vZWebqEa/aRFSpScZgYxc4KloNMkYZYHYo/OtAX01WUBO5cilbennNnUDeryy3FBc9p1/rv1a1BL9rY5wW2Kt4jYyp82lk+gZqtfHJDHHk44QLW7xq37AYd8JdQMjss="], "x5t": "eDziHrpDesOJXALdEuBF2tY4vWc", "x5t#S256": "__cmdM6AqteNxXRMH4daJGEsG15jZCsSxKTCwYk-PX4"}'
        >>>

        :returns: string
        """
        for item in self.jwks:
            if item["kid"] == kid:
                break
        return json.dumps(item)

    @staticmethod
    def construct_key(alg: str, jwk: str) -> bytes:
        """
        construct jwt algorithm instance from jwk

        :param alg: algorithm to be used
        :param jwk: signing key aka jwk
        :returns: key
        """
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
        """
        retrieve signing key and algorithm from given jwt header

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.parse_key_and_alg('eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJLRG9qblhUaF90Z0dzeWtDM1g4VjJfaEY3TU0zZlZpa1B6T2VDX2RiLWx3In0')
        (<cryptography.hazmat.backends.openssl.rsa._RSAPublicKey object at 0x101da7d90>, 'RS256')
        >>>

        :param header: jwt header
        :returns: key and algorithm
        """
        decoded_header: Dict = b64decode(header, deserialize=True)  # type: ignore
        kid = decoded_header["kid"]
        jwk = self.fetch_jwk(kid)
        alg = decoded_header["alg"]
        key = self.construct_key(alg, jwk)
        return key, alg

    def decode(self, token: str) -> Dict:
        """
        decode given json web token (jwt)

        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.decode(kc.access_token)
        {'jti': '39bd044e-88d7-470d-8a86-a1c11b6fb632', 'exp': 1584257028, 'nbf': 0, 'iat': 1584256968, 'iss': 'http://localhost:8080/auth/realms/master', 'aud': ['keycloak-client', 'account'], 'sub': '6ba08443-3881-40e7-af43-10b7196b02fd', 'typ': 'Bearer', 'azp': 'keycloak-client', 'auth_time': 0, 'session_state': '5e7d7225-0ec6-4581-a79a-0921b6f6301a', 'acr': '1', 'realm_access': {'roles': ['offline_access', 'uma_authorization']}, 'resource_access': {'keycloak-client': {'roles': ['uma_protection']}, 'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}}, 'scope': 'email profile', 'email_verified': False, 'clientId': 'keycloak-client', 'clientHost': '172.17.0.1', 'preferred_username': 'service-account-keycloak-client', 'clientAddress': '172.17.0.1'}
        >>>

        :param token: jwt to be decoded eg:access_token or refresh_token
        :returns: dictionary
        """
        header, body, signature = token.split(".")
        key, algorithm = self.parse_key_and_alg(header)
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            issuer=config.uma2.issuer,
            audience=config.client.client_id,
        )
