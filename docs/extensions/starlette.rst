Using Starlette Extension
=========================

.. code-block:: python
   :linenos:

    #! /usr/bin/env python
    import uvicorn

    from starlette.applications import Starlette
    from starlette.middleware.sessions import SessionMiddleware
    from starlette.responses import PlainTextResponse

    from keycloak.extensions.starlette import AuthenticationMiddleware


    app = Starlette()
    app.debug = True
    app.add_middleware(AuthenticationMiddleware, callback_url="http://localhost:8000/kc/callback", redirect_uri="/howdy", logout_uri="/logout")
    app.add_middleware(SessionMiddleware, secret_key="secret0123456789")


    @app.route("/howdy")
    def howdy(request):
        return PlainTextResponse("Howdy!")


    @app.route("/logout")
    def logout(request):
        return PlainTextResponse("User logged out!")


    if __name__ == "__main__":
        uvicorn.run(app)
