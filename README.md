[![Documentation Status](https://readthedocs.org/projects/keycloak-client/badge/?version=latest)](https://keycloak-client.readthedocs.io/en/latest/?badge=latest)
![CI](https://github.com/keycloak-client/keycloak-client/workflows/CI/badge.svg?branch=main)
[![PyPI version](https://badge.fury.io/py/keycloak.svg)](https://badge.fury.io/py/keycloak)
[![codecov](https://codecov.io/gh/keycloak-client/keycloak-client/branch/main/graph/badge.svg)](https://codecov.io/gh/keycloak-client/keycloak-client)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/keycloak.svg)](https://pypistats.org/packages/keycloak)

This repo contains a python client for [Keycloak](https://www.keycloak.org/).
Documentation is available in [https://keycloak-client.readthedocs.io](https://keycloak-client.readthedocs.io)


### Installation

```
pip install keycloak                       # install only client   
pip install "keycloak[docs]"               # install client + sphinx   
pip install "keycloak[extensions]"         # install client + django/flask/starlette   
pip install "keycloak[docs,extensions]"    # install client + sphinx + django/flask/starlette   
```

### Web Framework Support

We provide prebuilt middlewares for the following frameworks

* Flask
* Starlette
* Django
