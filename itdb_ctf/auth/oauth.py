import os
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"   # ← relaja la validación de scopes
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests


CLIENT_ID=os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET=os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI=os.environ["GOOGLE_REDIRECT_URI"]
SCOPES=["openid","email","profile"]  # mínimo privilegio: solo identidad    
CLIENT_CONFIG={
    "web":{
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris":[REDIRECT_URI]
    }
}

def _crear_flow() -> Flow:
    return Flow.from_client_config(
        CLIENT_CONFIG, 
        scopes=SCOPES, 
        redirect_uri=REDIRECT_URI, 
        autogenerate_code_verifier=False # ← desactiva PKCE

        )    
def url_de_autorizacion() -> tuple[str, str]:
    flow = _crear_flow()
    return flow.authorization_url(access_type="offline",include_granted_scopes="true",prompt="select_account")  # devuelve (url, state)

def canjear_codigo(code: str) -> dict:
    flow = _crear_flow()
    flow.fetch_token(code=code)
    return id_token.verify_oauth2_token(flow.credentials.id_token,g_requests.Request(), CLIENT_ID)
