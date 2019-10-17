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
    app.add_middleware(AuthenticationMiddleware, callback_uri="http://localhost:8000/kc/callback", redirect_uri="/howdy")
    app.add_middleware(SessionMiddleware, secret_key="adasdsadasdsad")


    @app.route("/")
    def howdy(request):
        return PlainTextResponse("Howdy")


    if __name__ == "__main__":
        uvicorn.run(app)
