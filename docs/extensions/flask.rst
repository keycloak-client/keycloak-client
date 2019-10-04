Using Flask Extension
=====================

.. code-block:: python
   :linenos:

   # -*- coding: utf-8 -*-
   from flask import Flask, session, Response

   from keycloak import KeycloakClient
   from keycloak.extensions.flask import Authentication


   # create flask app
   api = Flask(__name__)
   api.config["SECRET_KEY"] = "EYxuFcNqGamVU78GgfupoO5N4z2xokA58XtL0ag"


   # create keycloak client
   keycloak_client = KeycloakClient()


   # add authentication extension to flask app
   Authentication(api, keycloak_client)


   @api.route("/")
   def home():
       return Response("Welcome Home")


   if __name__ == "__main__":
       api.run(host="0.0.0.0", debug=True)
