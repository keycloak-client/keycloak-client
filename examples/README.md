Typical use case of keycloak consists of two parts

1. Authentication
2. Authorization

# Authentication

The authentication flow in keycloak server is as follows

* User hit the app
* App redirect user to keycloak login page
* User login in the keycloak 
* Keycloak redirects user to the callback URI of the app
* Callback URI handler retrieves authentication tokens from the keycloak server


# Authorization

Authorization is mostly implemented as a middleware within the app.
This middleware intercepts every request and see whether the user has permission to access that resource or not.
The pre-requisite for authorization is the RPT (Request Party Token) which needs to be retrieved first.

* Client / UI is supposed to send the RPT in all  API calls
* Middleware inside the app introspects the RPT and see whether it is valid


