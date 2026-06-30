import os 
import secrets 
import re 
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RUTA_ARCHIVOS=Path(os.environ.get("RUTA_ARCHIVOS_RETO", "./FILES_ITDB_CTF/retos" ))

def nombre_seguro(nombre: str) -> str:
    base = os.path.basename(nombre)
    return re.sub(r"[^A-Za-z0-9._-]","_",base)

def guardar_archivo(contenido: bytes, nombre_original: str) -> tuple[str, str]:
    limpio = nombre_seguro(nombre_original)
    _, ext = os.path.splitext(limpio)
    token = secrets.token_hex(8)
    nombre_fisico = f"LM{token}{ext}"
    RUTA_ARCHIVOS.mkdir(parents=True, exist_ok=True)
    ruta = RUTA_ARCHIVOS / nombre_fisico
    with ruta.open("wb") as f:
        f.write(contenido)
    return limpio,nombre_fisico

def borrar_archivo(nombre_fisico: str) -> bool:
    if not nombre_fisico:
        return False
    ruta = (RUTA_ARCHIVOS/nombre_fisico).resolve()

    if RUTA_ARCHIVOS.resolve() not in ruta.parents:
        return False
    
    if ruta.exists():
        ruta.unlink()
        return True
    return False
    