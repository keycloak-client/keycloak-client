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
    This class include methods that interact with the authorization api
    For details see https://www.keycloak.org/docs/5.0/authorization_services/index.html
    """

    _ticket: Dict = None  # type: ignore
    _rpt: Dict = {}

    @staticmethod
    def payload_for_client() -> Dict:
        """ method to generate payload for client """
        return {"grant_type": GrantTypes.client_credentials}

    @staticmethod
    def payload_for_user(username: str = None, password: str = None) -> Dict:
        """ method to generate payload for user """
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
        Method to retrieve protection api token (PAT).
        For more details see https://www.keycloak.org/docs/7.0/authorization_services/#_service_protection_whatis_obtain_pat

        >>> from keycloak import Client
        >>>
        >>> kc = Client()
        >>>
        >>> kc.pat()
        {'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHYkdydV9sa05wN29hdjg1MUx4LXRQT1c3LWdCeWRKRWZIYmUxRHp1Zm1NIn0.eyJqdGkiOiJmNDcyYTRlNC1iMTExLTQzYTgtOWU0OC04ZmZmMzAwYTFkZTciLCJleHAiOjE1NzIyNDQ5NDksIm5iZiI6MCwiaWF0IjoxNTcyMjQ0ODg5LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbInB5dGhvbi1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IkJlYXJlciIsImF6cCI6InB5dGhvbi1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJjYzJjMTQ1ZC0zNTc3LTRmNjItYTY1Zi02MTY3ZDk1ZDcxZGMiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiMTgwLjE1MS4xMzcuMTQwIiwiY2xpZW50SWQiOiJweXRob24tY2xpZW50IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtcHl0aG9uLWNsaWVudCIsImNsaWVudEFkZHJlc3MiOiIxODAuMTUxLjEzNy4xNDAiLCJlbWFpbCI6InNlcnZpY2UtYWNjb3VudC1weXRob24tY2xpZW50QHBsYWNlaG9sZGVyLm9yZyJ9.HilAGapGB8VeLN3hu2rdsUx-kJukfP9catlCshdaiS_L_FBKeJW-IKWHKNMNhPyT7xD9x5ToWW43rHY3pmVnHZwYrsr7_W31ee1qpSoHXR70RUcJ6w_JGw3Ce84oTjtpTDG2n2fzsOTT6hgym4NTT77Bj0asgiT2rHVWIgy2HZzMuonWQ44veT4yyae5QMvv0HxZkDOXExlFuLmK2rni2WpkVDUgzknMzUvrMTEhKRB5v7HUCHscPWfsMKo67eH9azF_hYW18ORiGQhJ92NDAiNK7-CeCH1dq5Cp9LkEfSlNnBNEiyrFZ9nsQbnbABoiun2iE_JJszsAnFjI95VOMg', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxOGQ1NzdiYy03MmY2LTRiMTUtYjc2Mi1hOGIzOWRjNzE2MjkifQ.eyJqdGkiOiIwMzA3NjliYi0yYTExLTRjM2UtODRhZi1kMjFiNmRiMmQ3NWQiLCJleHAiOjE1NzIyNDY2ODksIm5iZiI6MCwiaWF0IjoxNTcyMjQ0ODg5LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cHM6Ly9rZXljbG9hay5ha2hpbHB1dGhpcnkuZGV2L2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJweXRob24tY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiY2MyYzE0NWQtMzU3Ny00ZjYyLWE2NWYtNjE2N2Q5NWQ3MWRjIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUifQ.05pcfYObCCKLUCLrEcAsy-bXAdSLs8W-Toc3oETc65c', 'token_type': 'bearer', 'not-before-policy': 0, 'session_state': 'cc2c145d-3577-4f62-a65f-6167d95d71dc', 'scope': 'email profile'}

        Args:
            username (str): username to be used
            password (str): password to be used

        Returns:
            dict
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
        if not self._ticket:
            self._ticket = self.fetch_ticket(
                self.resources, self.access_token  # type: ignore
            )
        return self._ticket

    @handle_exceptions
    def fetch_ticket(self, resources: List = [], access_token: str = None) -> Dict:
        """
        Method to retrieve permission ticket.
        For details see https://www.keycloak.org/docs/7.0/authorization_services/#_service_protection_permission_api_papi

        >>> form keycloak import Client, Resource
        >>>
        >>> kc = Client()
        >>>
        >>> kc.find_ticket(kc.resources)
        {'ticket': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxOGQ1NzdiYy03MmY2LTRiMTUtYjc2Mi1hOGIzOWRjNzE2MjkifQ.eyJwZXJtaXNzaW9ucyI6W3sicnNpZCI6ImJiNmE3NzdmLWExN2ItNDU1NS1iMDM1LWE2Y2UxMmExZmQyMSJ9XSwianRpIjoiODgyY2JiZDgtMTc5MS00NGFjLTk1YzgtMWI2NTExYjIwNmJkLTE1NzIyNDYwNTI0NTQiLCJleHAiOjE1NzIyNDYwOTUsIm5iZiI6MCwiaWF0IjoxNTcyMjQ2MDM1LCJhdWQiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwic3ViIjoiZTFmYmQ3ZDYtYWQyYi00MDdmLTg5Y2YtNmMyYjAwNGQ3OGJiIiwiYXpwIjoicHl0aG9uLWNsaWVudCJ9.rS0ACmDH8WymeIEIJa-3CfVgheeZ2kqUvBNYJWIrRZc'}


        Args:
            resources (list): list of resources
            access_token (str): access token to be used

        Returns:
            dict
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
        if not self._rpt:
            self._rpt = self.fetch_rpt(self.ticket, self.access_token)  # type: ignore
        return self._rpt

    @handle_exceptions
    def fetch_rpt(self, ticket: str = None, access_token: str = None) -> Dict:
        """
        Method to fetch the request party token.
        For details see https://www.keycloak.org/docs/5.0/authorization_services/#_service_rpt_overview

        >>> form keycloak import Client, Resource
        >>>
        >>> kc = Client()
        >>>
        >>> resources = [
        >>>     Resource("8762039c-cdfa-4ef9-9f70-45248863c4da", ["create", "read"])
        >>> ]
        >>>
        >>> ticket = kc.find_ticket(resources)
        >>>
        >>> kc.rpt(ticket["ticket"])
        {'upgraded': False, 'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHYkdydV9sa05wN29hdjg1MUx4LXRQT1c3LWdCeWRKRWZIYmUxRHp1Zm1NIn0.eyJqdGkiOiIzZTg3OGNkNy1iNjZkLTQyOGItYjQ0ZS05YTRkNjE4NzA2NTAiLCJleHAiOjE1NzIyNDY1NTcsIm5iZiI6MCwiaWF0IjoxNTcyMjQ2NDk3LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbInB5dGhvbi1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IkJlYXJlciIsImF6cCI6InB5dGhvbi1jbGllbnQiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJiZWM3NGI4MC02MDJlLTQzZTktYjBlMS1jYTQ5YzA1YWI0OGUiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJhdXRob3JpemF0aW9uIjp7InBlcm1pc3Npb25zIjpbeyJyc2lkIjoiYmI2YTc3N2YtYTE3Yi00NTU1LWIwMzUtYTZjZTEyYTFmZDIxIiwicnNuYW1lIjoiRGVmYXVsdCBSZXNvdXJjZSJ9XX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImNsaWVudEhvc3QiOiIxODAuMTUxLjEzNy4xNDAiLCJjbGllbnRJZCI6InB5dGhvbi1jbGllbnQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1weXRob24tY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE4MC4xNTEuMTM3LjE0MCIsImVtYWlsIjoic2VydmljZS1hY2NvdW50LXB5dGhvbi1jbGllbnRAcGxhY2Vob2xkZXIub3JnIn0.UmMaTi-x-tX71iWovQ8gupFdzpJ7YLOSQsAPPLlhaKLbHFDci0w1C99IXAcVkDyKzTgGfs-2SQzPsS5hYQzy_hZP5d-jqWxOvq_iBx5Nem1ccKrfUmkpHDsNDB7BV-me6g8jp0uPOMq4pPTR5elJ8YEho_TS_QKqsD-N3yNLhQgxVtELWGovgjmnbuLmglKoNLktBYoJTukoWkwpNCXFuJSbbujUrHcsQ1bb14LXZrDJ15_EreO3JpWMtt-lR9H-6MH56StKQ7OKhp3CK7zIOreNW8kZfGCoqGzWMotDGQXDYZsL4DjtIzuSgkeI63culrN70ZIA0M89klrqX9ZpFw', 'expires_in': 60, 'refresh_expires_in': 1800, 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxOGQ1NzdiYy03MmY2LTRiMTUtYjc2Mi1hOGIzOWRjNzE2MjkifQ.eyJqdGkiOiI3YWFkOTZjNy1jYmI0LTQyNzUtODkyMi01MjNhN2M1MDBlYzQiLCJleHAiOjE1NzIyNDgyOTcsIm5iZiI6MCwiaWF0IjoxNTcyMjQ2NDk3LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmFraGlscHV0aGlyeS5kZXYvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXVkIjoiaHR0cHM6Ly9rZXljbG9hay5ha2hpbHB1dGhpcnkuZGV2L2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6ImUxZmJkN2Q2LWFkMmItNDA3Zi04OWNmLTZjMmIwMDRkNzhiYiIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJweXRob24tY2xpZW50IiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiYmVjNzRiODAtNjAyZS00M2U5LWIwZTEtY2E0OWMwNWFiNDhlIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJweXRob24tY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJhdXRob3JpemF0aW9uIjp7InBlcm1pc3Npb25zIjpbeyJyc2lkIjoiYmI2YTc3N2YtYTE3Yi00NTU1LWIwMzUtYTZjZTEyYTFmZDIxIiwicnNuYW1lIjoiRGVmYXVsdCBSZXNvdXJjZSJ9XX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSJ9.woXfkz49D13Fzxqaii9Gh3dr2ZiGHNA2grq2z9nYNqc', 'token_type': 'Bearer', 'not-before-policy': 0}

        Args:
            ticket (str): permission ticket
            access_token (str): access token to be used

        Returns:
            dict
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
        Method to introspect the request party token.
        For details see https://www.keycloak.org/docs/5.0/authorization_services/#_service_protection_token_introspection

        >>> form keycloak import Client, Resource
        >>>
        >>> kc = Client()
        >>>
        >>> resources = [
        >>>     Resource("8762039c-cdfa-4ef9-9f70-45248863c4da", ["create", "read"])
        >>> ]
        >>>
        >>> ticket = kc.find_ticket(resources)
        >>>
        >>> rpt = kc.rpt(ticket["ticket"])
        >>>
        >>> kc.introspect(rpt["access_token"])
        {'jti': '5a948d88-d8ef-4730-ad4f-a7f82604c196', 'exp': 1572246750, 'nbf': 0, 'iat': 1572246690, 'aud': ['python-client', 'account'], 'typ': 'Bearer', 'auth_time': 0, 'acr': '1', 'permissions': [{'rsid': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'rsname': 'Default Resource', 'resource_id': 'bb6a777f-a17b-4555-b035-a6ce12a1fd21', 'resource_scopes': []}], 'active': True}

        Args:
            rpt (str): rpt token

        Returns:
            dict
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
