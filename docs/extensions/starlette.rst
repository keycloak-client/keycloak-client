Using Starlette Extension
=========================

.. code-block:: python
   :linenos:

   # -*- coding: utf-8 -*-
   import uvicorn

   from keycloak.extensions.starlette import Authentication

   from starlette.applications import Starlette
   from starlette.middleware.sessions import SessionMiddleware
   from starlette.responses import PlainTextResponse

   app = Starlette()
   app.debug = True
   app.add_middleware(Authentication)
   app.add_middleware(SessionMiddleware, secret_key="faaa5490558e4ec5aa74f6f8b36ffc77")


   @app.route("/")
   def index(request, **kwargs):
       return PlainTextResponse("Howdy!")


   if __name__ == "__main__":
       uvicorn.run(app, debug=True)
