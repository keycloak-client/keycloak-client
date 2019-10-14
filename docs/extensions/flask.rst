Using Flask Extension
=====================

.. code-block:: python
   :linenos:

   # -*- coding: utf-8 -*-
   from flask import Flask, session, Response

   from keycloak import Client
   from keycloak.extensions.flask import Authentication


   # create flask app
   api = Flask(__name__)
   api.config["SECRET_KEY"] = "EYxuFcNqGamVU78GgfupoO5N4z2xokA58XtL0ag"


   # create keycloak client
   kc = Client()


   # add authentication plugin
   Authentication(api, kc)


   @api.route("/info")
   def user_info():
       user = session["user"]
       return Response(user)

   @api.route("/tokens")
   def user_tokens():
       tokens = session["tokens"]
       return Response(tokens)


   if __name__ == "__main__":
       api.run(host="0.0.0.0", debug=True)
