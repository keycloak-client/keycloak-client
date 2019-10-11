#! /usr/bin/env python
# -*- coding: utf-8 -*-

from keycloak import KeycloakClient

kc = KeycloakClient()


pat = kc.pat()
print("PAT success")

resources = kc.resources(pat["access_token"])
for resource in resources:
    print(kc.resource(resource, pat["access_token"]))

exit()

resources = (
    {
        "resource_id": "5e6c4b9e-6691-4d8f-9bdb-5fd0b63ec37e",
        "resource_scopes": ["view"],
    },
)
ticket = kc.ticket(resources, pat["access_token"])
print("Ticket success")


rpt = kc.rpt(ticket["ticket"], pat["access_token"])
print("RPT success")


access_token = kc.decode(rpt["access_token"])
print(access_token)
permissions = access_token.get("authorization", {}).get("permissions", [])
print(permissions)
