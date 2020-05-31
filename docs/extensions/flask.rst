Using Flask Extension
=====================

.. code-block:: python
   :linenos:

    #! /usr/bin/env python
    from flask import Flask

    from keycloak.extensions.flask import AuthenticationMiddleware

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret0123456789"


    app.wsgi = AuthenticationMiddleware(
        app.wsgi,
        app.config,
        app.session_interface,
        callback_url="http://localhost:5000/kc/callback",
        redirect_uri="/howdy",
        logout_uri="/logout"
    )


    @app.route("/howdy")
    def howdy():
        return "Howdy!"

    @app.route("/logout")
    def logout():
        return "User logged out!"


    if __name__ == "__main__":
        app.run(debug=True)
