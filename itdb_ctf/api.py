import os 
import reflex as rx

from pathlib import Path
from sqlmodel import Session
from itdb_ctf.db import engine
from itdb_ctf.models import Reto
from itdb_ctf.retos.archivo_logic import RUTA_ARCHIVOS
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, FileResponse

from itdb_ctf.auth.oauth import url_de_autorizacion, canjear_codigo
from itdb_ctf.auth.auth_logic import obtener_crear_usuario, DominiNoPermitido
from itdb_ctf.auth.jwt_utils import emitir_jwt, validar_jwt

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
    resp = RedirectResponse("http://localhost:3000/retos")

    resp.set_cookie("token", token, max_age= 3600)
    resp.delete_cookie("oauth_state")
    return resp

@fastapi_app.get("/api/reto/{id_reto}/descarga")
async def descarga_reto(id_reto:int, request: Request):
    # autenticar JWT
    token=request.cookies.get("token")
    if not token or not validar_jwt(token):
        raise HTTPException(status_code=401,detail="no autenticado")
    #busqueda de archivo_reto
    with Session(engine) as s:
        reto = s.get(Reto,id_reto)
        if not reto or not reto.archivo_original or not reto.archivo_ruta:
            raise HTTPException(status_code=404, detail="404")
        nombre_amigable=reto.archivo_original or "archivo"
        nombre_fisico=reto.archivo_ruta
    # Recontrimos ruta 
    ruta =  RUTA_ARCHIVOS / nombre_fisico
    if not ruta.exists():
        raise HTTPException(status_code=404,detail="404")
    # Servimos el archivo con el nombre amigable
    return FileResponse(ruta,filename=nombre_amigable)



###---AÑADIR SEGURIDAD A LA CREACIÓN DE COOKIES
app = rx.App(api_transformer=fastapi_app)
