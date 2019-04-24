Authentication
==============

Keycloak client provides two methods called `authentication_url` and `authentication_callback`,
using which you can connect to the authentication endpoints of keycloak server easily.

The following snippet is an example written in `Flask <http://flask.pocoo.org/>`_ framework

.. code-block:: python
   :linenos:
   :emphasize-lines: 4,11

   @app.route('/login', methods=['GET'])
   def login():
       """ Endpoint to initiate authentication """
       auth_url = keycloak_client.authentication_url()
       return redirect(auth_url)


   @app.route('/login-callback', methods=['GET'])
   def login_callback():
       """ Endpoint to retrieve authentication tokens """
       code = request.args.get('code')
       tokens = keycloak_client.authentication_callback(code)
       return jsonify(tokens)
