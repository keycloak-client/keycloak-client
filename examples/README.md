# Different Auth workflows that can be acheived by this client

## Authentication flow

* Initiate login by redirecting user to the keycloak login page
* Once the user is authenticated, keycloak redirects the user back to the callback URL with a `code`
* Parse the `code` from URL and retrieve the `AAT` from keycloak server

## Authorization flow

* `AAT` (Authentication) is a pre-requisite for authorization flow
* Register resources in the keycloak server
* User tries to access the resource using `AAT`
* Middleware introspects the `AAT`
* Middleware then allow or deny access to the resource
