Using Flask Extension
=====================

.. code-block:: python
   :linenos:

    #! /usr/bin/env python
    from flask import Flask
    from keycloak.extensions.flask import Authentication


    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret123456789"
    Authentication(app, callback_uri="http://localhost:5000/kc/callback", redirect_uri="/howdy")


    @app.route("/howdy")
    def howdy():
        return "Howdy!"


    if __name__ == "__main__":
        app.run(debug=True)
