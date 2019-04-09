# Standard workflows implemented in the examples

## Authentication flow

* App needs to initiate login by redirecting to the keycloak login page
* Once user is authenticated successfully, keycloak redirects the user back to the callback URL with a `code`
* App needs to parse the `code` from URL and retrieve the `AAT` from keycloak server

## Authorization flow

* `AAT` is a pre-requisite for authorization
* App needs to retrieve the `Permission ticket`
* App needs to retrieve the `RPT` using `AAT` and `Permission ticket`
* App needs to check permissions inside `RPT` and need to control user access to resources
