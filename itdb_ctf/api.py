import reflex as rx 
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from itdb_ctf.auth.oauth import url_de_autorizacion, canjear_codigo
from itdb_ctf.auth.auth_logic import obtener_crear_usuario, DominiNoPermitido
from itdb_ctf.auth.jwt_utils import emitir_jwt

fastapi_app = FastAPI()


@fastapi_app.get("/auth/login")
async def login_oauth():
    url, state = url_de_autorizacion()
    resp = RedirectResponse(url)
    resp.set_cookie("oauth_state",state,httponly=True, max_age=600)
    return resp

@fastapi_app.get("/auth/callback")
async def callback(request: Request, code: str, state: str):
    if request.cookies.get("oauth_state") != state:
        return RedirectResponse("/login?error=csrf")
    info = canjear_codigo(code)
    try: 
        usuario = obtener_crear_usuario(info)
    except DominiNoPermitido:
        return RedirectResponse("/login?error=dominio")
    token = emitir_jwt(usuario)
    resp = RedirectResponse("/retos")

    resp.set_cookie("token", token, max_age= 3600)
    resp.delete_cookie("oauth_state")
    return resp

###---AÑADIR SEGURIDAD A LA CREACIÓN DE COOKIES
app = rx.App(api_transformer=fastapi_app)
