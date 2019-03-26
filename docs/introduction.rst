Introduction
============

Keycloak is a open source identity and access management solution for modern
application and services. It has many great features like,

* Single sign on
* Identity Federation
* Social login
* Standard protocols etc.

To know more about keycloak, please visit their
official website [here](https://www.keycloak.org/).

Keycloak community provides [client adapters](https://www.keycloak.org/docs/5.0/securing_apps/index.html#what-are-client-adapters)
which helps in keycloak integration with different langauges and frameworks like Java, Python, JBOSS etc.
For Java they have very mature adapter where as for Python they do not have a proper adapter which supports all/major functionalities.
That's the reason why I started writing this library.


Common Keycloak Workflows
====================

The common keycloak workflows include the following

* Authentication - Identifying the user (behind the screen it could be anything LDAP, Social login etc)
* Authorization - Identifying whether the user has permission to access the resource or not
* Resource management - What all resources are available within the server and how it needs to be managed
