[![Documentation Status](https://readthedocs.org/projects/keycloak-client/badge/?version=latest)](https://keycloak-client.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/akhilputhiry/keycloak-client.svg?branch=master)](https://travis-ci.com/akhilputhiry/keycloak-client)
[![PyPI version](https://badge.fury.io/py/keycloak.svg)](https://badge.fury.io/py/keycloak)
[![codecov](https://codecov.io/gh/akhilputhiry/keycloak-client/branch/master/graph/badge.svg)](https://codecov.io/gh/akhilputhiry/keycloak-client)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/keycloak.svg)](https://pypistats.org/packages/keycloak)

This repo contains a python client for [Keycloak](https://www.keycloak.org/) IAM
Visit [https://keycloak-client.readthedocs.io](https://keycloak-client.readthedocs.io) for documentation

### Examples

```python

from keycloak import Client

kc = Client()

# generate pat for clients
pat = kc.pat()

# generate pat for users
pat = kc.pat("username", "password")

# generate permissiong ticket
resources = [{
    "resource_id": "",
    "resource_scopes: []
}]
ticket = kc.ticket(resources, pat["access_token"])

# generate rpt
rpt = kc.rpt(ticket["ticket"], pat["access_token"])

# introspect rpt
kc.introspect(rpt, access_token=pat["access_token"])
```

### UMA Workflow

![Workflow](http://www.janua.fr/wp-content/uploads/2019/05/understandinf-UMA-and-Keycloak.png)
