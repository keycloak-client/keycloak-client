# -*- coding: utf-8 -*-
import logging
from dataclasses import asdict
from typing import Tuple, Dict, List

import requests

from ..config import config
from ..constants import Logger, TokenType, GrantTypes, TokenTypeHints
from ..utils import auth_header, basic_auth, handle_exceptions


log = logging.getLogger(Logger.name)


class AuthorizationMixin:
    """
    collection of methods to interact with the authorization api
    see https://www.keycloak.org/docs/latest/authorization_services/ for details
    """

    _ticket: Dict = None  # type: ignore
    _rpt: Dict = {}

    @staticmethod
    def payload_for_client() -> Dict:
        """
        generate payload for keycloak client

        :returns: dictionary
        """
        return {"grant_type": GrantTypes.client_credentials}

    @staticmethod
    def payload_for_user(username: str = None, password: str = None) -> Dict:
        """
        generate payload for keycloak user

        :param username: username to be used
        :param password: password to be used

        :returns: dictionary
        """
        if username and password:
            return {
                "grant_type": GrantTypes.password,
                "username": username,
                "password": password,
            }
        else:
            return {}

    @staticmethod
    @handle_exceptions
    def pat(username: str = None, password: str = None) -> Dict:
        """
        retrieve protection api token (PAT),
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_service_protection_whatis_obtain_pat>`__ for more details

        >>>
        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.pat()
        {'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmMTNTUndXVGxRQnFmNmNoamM4SHRtY09sN3NpaTNpaGVXaFNLX0hla280In0.eyJqdGkiOiIzNDliZmQ1ZC1jZDZjLTRjZDAtOTM3Mi1lNzE2N2Y5NGEyMDkiLCJleHAiOjE1ODQxODU0MDcsIm5iZiI6MCwiaWF0IjoxNTg0MTg1MzQ3LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbImtleWNsb2FrLWNsaWVudCIsImFjY291bnQiXSwic3ViIjoiNGM5YzI0MzAtYjJlNy00ZjBiLTkzMjUtYWE4MWRmZmUwNDYzIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoia2V5Y2xvYWstY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiYWY3N2JmOTEtNTQ2ZC00M2E1LTgwZmYtYzQ0MDg2MDVhNTlmIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsia2V5Y2xvYWstY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRJZCI6ImtleWNsb2FrLWNsaWVudCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6IjE3Mi4xNy4wLjEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQta2V5Y2xvYWstY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xNy4wLjEifQ.PUq6-N-9Hn57kSrK0-6reC8AYT08EV4DZsBqxQ7D0cyp4hHTSP5ax9zQwn0Q05bCZ3c_L_prwMa8VOEFF5Nv-ch2otVg7lIqTc4xeLORSRmIxhjFSxLbiXwBhl4mmfOOHwSL0yBRVHhPzdRkHyVmLlq1WrPfiNe6NRuhDiQIIaFTA0-jSfyqtXNcYjcidsTwjL0q9_Cxt0BrsjTQZLO2b9NKnh5rKbBewvwwIWvZqY5j8QiT3LL652RAED_q7RbG-jFqtLleEklKTtS3bFlJIMCzvdOmfTxZT-FY2zbx_0NJil8bQTJorwveF6Vjb11vAuTI9ccjaOg54SFQT3tSGQ', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI5MmE5NTI2NC0wNTAyLTQzN2ItYWE3ZS01ZGIwNjFlYzMwOWYifQ.eyJqdGkiOiJhYjU2NTg1OS1hODJkLTQzMzYtOTFmNS1kNTU0OWU2ZTU0YTkiLCJleHAiOjE1ODQxODcxNDcsIm5iZiI6MCwiaWF0IjoxNTg0MTg1MzQ3LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6IjRjOWMyNDMwLWIyZTctNGYwYi05MzI1LWFhODFkZmZlMDQ2MyIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJrZXljbG9hay1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJhZjc3YmY5MS01NDZkLTQzYTUtODBmZi1jNDQwODYwNWE1OWYiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImtleWNsb2FrLWNsaWVudCI6eyJyb2xlcyI6WyJ1bWFfcHJvdGVjdGlvbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIn0.vdL4dCB8GLa-045EO3_UNUfDWMTOvoDnFs9giRjrvQM', 'token_type': 'bearer', 'not-before-policy': 0, 'session_state': 'af77bf91-546d-43a5-80ff-c4408605a59f', 'scope': 'email profile'}
        >>>

        :param username: username to be used
        :param password: password to be used

        :returns: dictionary
        """
        headers = basic_auth(config.client.client_id, config.client.client_secret)
        payload = (
            AuthorizationMixin.payload_for_user(username, password)
            or AuthorizationMixin.payload_for_client()
        )
        log.debug("Retrieving PAT from server")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        return response.json()

    @property
    def ticket(self) -> Dict:
        """
        permission ticket retrieved from server

        :returns: dictionary
        """
        if not self._ticket:
            self._ticket = self.fetch_ticket(
                self.resources, self.access_token  # type: ignore
            )
        return self._ticket

    @handle_exceptions
    def fetch_ticket(self, resources: List = [], access_token: str = None) -> Dict:
        """
        retrieve permission ticket from keycloak server
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_overview_terminology_permission_ticket>`__ for more details

        >>>
        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.fetch_ticket(kc.resources)
        {'ticket': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI5MmE5NTI2NC0wNTAyLTQzN2ItYWE3ZS01ZGIwNjFlYzMwOWYifQ.eyJwZXJtaXNzaW9ucyI6W3sicnNpZCI6IjQ4MTUyMTI2LWFhOTEtNGE0Zi04ZWU4LTczOTI4ZjViNmMwMCJ9XSwianRpIjoiNDhlZmVmZDQtMDg5NC00NjA2LTk0YjUtMDhlNjZiNTE4YWM2LTE1ODQxODUyOTUyMzkiLCJleHAiOjE1ODQxODUzNTUsIm5iZiI6MCwiaWF0IjoxNTg0MTg1Mjk1LCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvbWFzdGVyIiwic3ViIjoiNGM5YzI0MzAtYjJlNy00ZjBiLTkzMjUtYWE4MWRmZmUwNDYzIiwiYXpwIjoia2V5Y2xvYWstY2xpZW50In0.Or_6wzK9wlQMBPpi8bWIioWCeO6QuolKjr4mKC4YWpA'}
        >>>

        :param resources: list of resources
        :param access_token: access token to be used

        :returns: dictionary
        """
        access_token = access_token or self.access_token  # type: ignore
        resources = resources or self.resources  # type: ignore
        headers = auth_header(access_token, TokenType.bearer)
        payload = [
            {"resource_id": x["_id"], "resource_scopes": x["resource_scopes"]}
            for x in resources
        ]
        log.debug("Retrieving permission ticket from keycloak")
        response = requests.post(
            config.uma2.permission_endpoint, json=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("Permission ticket retrieved successfully")
        return response.json()

    @property
    def rpt(self) -> Dict:
        """
        request party token retrieved from server

        :returns: dictionary
        """
        if not self._rpt:
            self._rpt = self.fetch_rpt(self.ticket, self.access_token)  # type: ignore
        return self._rpt

    @handle_exceptions
    def fetch_rpt(self, ticket: str = None, access_token: str = None) -> Dict:
        """
        retrieve request party token (RPT)
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_service_rpt_overview>`__ for more details

        >>>
        >>> form keycloak import Client, Resource
        >>> kc = Client()
        >>> ticket = kc.find_ticket(kc.resources)
        >>> kc.rpt(ticket["ticket"])
        {'upgraded': False, 'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHYkdydV9sa05wN29hdjg1MUx4LXRQT1c3LWdCeWRKRWZIYmUxRHp1Zm1NIn0.eyJqdGkiOiIzZTg3OGNkNy1iNjZkLTQyOGItYjQ0ZS05YTRkNjE4NzA2NTAiLCJleHAiOjE1NzIyNDY1NTcsIm5iZiI6MCwiaWF0IjoxNTcyMjQ2NDk3LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbInB5dGhvbi1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IkJlYXJlciIsImF6cCI6InB5dGhvbi1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJiZWM3NGI4MC02MDJlLTQzZTktYjBlMS1jYTQ5YzA1YWI0OGUiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJhdXRob3JpemF0aW9uIjp7InBlcm1pc3Npb25zIjpbeyJyc2lkIjoiYmI2YTc3N2YtYTE3Yi00NTU1LWIwMzUtYTZjZTEyYTFmZDIxIiwicnNuYW1lIjoiRGVmYXVsdCBSZXNvdXJjZSJ9XX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImNsaWVudEhvc3QiOiIxODAuMTUxLjEzNy4xNDAiLCJjbGllbnRJZCI6InB5dGhvbi1jbGllbnQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1weXRob24tY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE4MC4xNTEuMTM3LjE0MCIsImVtYWlsIjoic2VydmljZS1hY2NvdW50LXB5dGhvbi1jbGllbnRAcGxhY2Vob2xkZXIub3JnIn0.UmMaTi-x-tX71iWovQ8gupFdzpJ7YLOSQsAPPLlhaKLbHFDci0w1C99IXAcVkDyKzTgGfs-2SQzPsS5hYQzy_hZP5d-jqWxOvq_iBx5Nem1ccKrfUmkpHDsNDB7BV-me6g8jp0uPOMq4pPTR5elJ8YEho_TS_QKqsD-N3yNLhQgxVtELWGovgjmnbuLmglKoNLktBYoJTukoWkwpNCXFuJSbbujUrHcsQ1bb14LXZrDJ15_EreO3JpWMtt-lR9H-6MH56StKQ7OKhp3CK7zIOreNW8kZfGCoqGzWMotDGQXDYZsL4DjtIzuSgkeI63culrN70ZIA0M89klrqX9ZpFw', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxOGQ1NzdiYy03MmY2LTRiMTUtYjc2Mi1hOGIzOWRjNzE2MjkifQ.eyJqdGkiOiI3YWFkOTZjNy1jYmI0LTQyNzUtODkyMi01MjNhN2M1MDBlYzQiLCJleHAiOjE1NzIyNDgyOTcsIm5iZiI6MCwiaWF0IjoxNTcyMjQ2NDk3LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cHM6Ly9rZXljbG9hay5ha2hpbHB1dGhpcnkuZGV2L2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJweXRob24tY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiYmVjNzRiODAtNjAyZS00M2U5LWIwZTEtY2E0OWMwNWFiNDhlIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJhdXRob3JpemF0aW9uIjp7InBlcm1pc3Npb25zIjpbeyJyc2lkIjoiYmI2YTc3N2YtYTE3Yi00NTU1LWIwMzUtYTZjZTEyYTFmZDIxIiwicnNuYW1lIjoiRGVmYXVsdCBSZXNvdXJjZSJ9XX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSJ9.woXfkz49D13Fzxqaii9Gh3dr2ZiGHNA2grq2z9nYNqc', 'token_type': 'Bearer', 'not-before-policy': 0}
        >>>

        :param ticket: permission ticket
        :param access_token: access token to be used

        :returns: dictionary
        """
        ticket = ticket or self.fetch_ticket()["ticket"]
        access_token = access_token or self.access_token  # type: ignore
        payload = {"grant_type": GrantTypes.uma_ticket, "ticket": ticket}
        headers = auth_header(access_token, TokenType.bearer)
        log.debug("Retrieving RPT from keycloak")
        response = requests.post(
            config.uma2.token_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("RPT retrieved successfully")
        return response.json()

    @staticmethod
    @handle_exceptions
    def introspect(rpt: str) -> Dict:
        """
        introspect the request party token (RPT)
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_service_protection_token_introspection>`__ for more details

        >>>
        >>> form keycloak import Client, Resource
        >>> kc = Client()
        >>> ticket = kc.find_ticket(resources)
        >>> rpt = kc.rpt(ticket["ticket"])
        >>> kc.introspect(rpt["access_token"])
        {'jti': '5a948d88-d8ef-4730-ad4f-a7f82604c196', 'exp': 1572246750, 'nbf': 0, 'iat': 1572246690, 'aud': ['python-client', 'account'], 'typ': 'Bearer', 'auth_time': 0, 'acr': '1', 'permissions': [{'rsid': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'rsname': 'Default Resource', 'resource_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'resource_scopes': []}], 'active': True}
        >>>

        :param rpt: rpt token

        :returns: dictionary
        """
        payload = {"token_type_hint": TokenTypeHints.rpt, "token": rpt}
        headers = basic_auth(config.client.client_id, config.client.client_secret)
        log.debug("Introspecting RPT token")
        response = requests.post(
            config.uma2.introspection_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("RPT introspected successfully")
        return response.json()
