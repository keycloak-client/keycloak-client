# -*- coding: utf-8 -*-
import logging
from dataclasses import asdict
from typing import Dict, List, Tuple

import httpx

from keycloak.config import config
from keycloak.constants import GrantTypes, Logger, TokenType, TokenTypeHints
from keycloak.utils import auth_header, basic_auth, handle_exceptions

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
        response = httpx.post(config.uma2.token_endpoint, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    @handle_exceptions
    def ticket(self, resources: List = [], access_token: str = None) -> Dict:
        """
        retrieve permission ticket from keycloak server
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_overview_terminology_permission_ticket>`__ for more details

        >>>
        >>> from keycloak import Client
        >>> kc = Client()
        >>> kc.ticket(kc.resources)
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
        response = httpx.post(
            config.uma2.permission_endpoint, json=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("Permission ticket retrieved successfully")
        return response.json()

    @handle_exceptions
    def rpt(self, access_token: str) -> Dict:
        """
        retrieve request party token (RPT)
        see `docs <https://www.keycloak.org/docs/latest/authorization_services/#_service_rpt_overview>`__ for more details

        >>>
        >>> form keycloak import Client
        >>> kc = Client(username='myuser', password='*****')
        >>> kc.rpt(kc.access_token)
        2020-08-03 11:47:54,568 [DEBUG] Retrieving RPT from keycloak
        2020-08-03 11:47:54,581 [DEBUG] RPT retrieved successfully
        2020-08-03 11:47:54,581 [DEBUG] Retrieving JWKs from keycloak server
        2020-08-03 11:47:54,587 [DEBUG] JWKs retrieved successfully
        {'exp': 1596435534, 'iat': 1596435474, 'jti': '822c7f6f-cd0a-4b9d-b55c-72803755ca7c', 'iss': 'http://localhost:8080/auth/realms/master', 'aud': ['kc', 'account'], 'sub': 'fce7f440-2e40-4161-90b4-61a1913c4b28', 'typ': 'Bearer', 'azp': 'kc', 'session_state': 'b3498962-3973-4f2d-9150-b1338e974d08', 'acr': '1', 'realm_access': {'roles': ['offline_access', 'uma_authorization']}, 'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}}, 'authorization': {'permissions': [{'rsid': '992dfa45-6098-45ac-b62e-da4d2787377f', 'rsname': 'Default Resource'}]}, 'scope': 'profile email', 'email_verified': True, 'preferred_username': 'akhilputhiry'}
        >>>

        :param access_token: access token to be used

        :returns: dictionary
        """
        payload = {
            "grant_type": GrantTypes.uma_ticket,
            "audience": config.client.client_id,
        }
        headers = auth_header(access_token, TokenType.bearer)
        log.debug("Retrieving RPT from keycloak")
        response = httpx.post(config.uma2.token_endpoint, data=payload, headers=headers)
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
         >>> form keycloak import Client
        >>> kc = Client(username='myuser', password='*****')
        >>> rpt = kc.rpt(kc.access_token)
        >>> kc.introspect(rpt['access_token'])
        2020-08-03 11:47:54,628 [DEBUG] Introspecting RPT token
        2020-08-03 11:47:54,635 [DEBUG] RPT introspected successfully
        {'exp': 1596435534, 'nbf': 0, 'iat': 1596435474, 'jti': '822c7f6f-cd0a-4b9d-b55c-72803755ca7c', 'aud': ['kc', 'account'], 'typ': 'Bearer', 'acr': '1', 'permissions': [{'rsid': '992dfa45-6098-45ac-b62e-da4d2787377f', 'rsname': 'Default Resource', 'resource_id': '992dfa45-6098-45ac-b62e-da4d2787377f', 'resource_scopes': []}], 'active': True}
        >>>

        :param rpt: rpt token

        :returns: dictionary
        """
        payload = {"token_type_hint": TokenTypeHints.rpt, "token": rpt}
        headers = basic_auth(config.client.client_id, config.client.client_secret)
        log.debug("Introspecting RPT token")
        response = httpx.post(
            config.uma2.introspection_endpoint, data=payload, headers=headers
        )
        response.raise_for_status()
        log.debug("RPT introspected successfully")
        return response.json()
