import os
import datetime
import jwt

SECRET=os.environ["JWT_SECRET_KEY"]
ALGORITHM=os.environ.get("JWT_ALGORITHM","HS256")
EXPIRE_MIN=int(os.environ.get("JWT_EXPIRE_MINUTE","60"))

def emitir_jwt(usuario):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub":str(usuario.id_usuario),
        "rol":usuario.id_rol,
        "iat":now,
        "exp":now+datetime.timedelta(minutes=EXPIRE_MIN),
    }
    return jwt.encode(payload,SECRET,algorithm=ALGORITHM)


def validar_jwt(token:str) -> dict | None:
    try:
        return jwt.decode(token,SECRET,algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
