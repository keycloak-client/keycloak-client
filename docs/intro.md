**************************
Keycloak client |version|
**************************

`Keycloak <https://www.keycloak.org/>`_ is an open source identity and access management (IAM)
solution for the modern application and services. To know more about keycloak, please visit
their official website. The focus of this library is to provide easy integration with keycloak
server, so that the features like authentication, authorization etc can be used in a python
applications very easily.


Examples
********

https://github.com/keycloak-client/keycloak-client/tree/master/examples


Implementation
**************

This library consists of two sections

* Core APIs
* Extensions

Core APIs
*********

These consists of the core interactions with the keycloak server.


Extensions
**********

These consists of middleware implementations for standard frameworks like Flask, Django etc.
Extensions are implemented using core APIs.
While integrating keycloak with your app, either you can use the core APIs directly or you can use prebuilt extensions.
