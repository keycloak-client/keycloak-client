# -*- coding: utf-8 -*-
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import PlainTextResponse
from keycloak.extensions.starlette import AuthenticationMiddleware


app = Starlette()
app.add_middleware(
    AuthenticationMiddleware,
    callback_url="http://localhost:8000/kc/callback",
    login_redirect_uri="/home",
    logout_redirect_uri="/logout",
)
app.add_middleware(SessionMiddleware, secret_key="key0123456789")


@app.route("/home")
def home(request):
    user = request.session["user"]
    return PlainTextResponse(f"Howdy {user}!")


@app.route("/logout")
def logout(request):
    return PlainTextResponse("User logged out successfully")


if __name__ == "__main__":
    uvicorn.run(app)
