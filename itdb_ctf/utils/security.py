from abc import ABC, abstractmethod
import bcrypt
import hashlib  


class HasherBase(ABC):

    @abstractmethod
    def hashear (self, cadena:str)->str:  # GENERAR HASH DE CADENA DE TEXTO
        ...
    
    @abstractmethod
    def verificar(self, cadena:str, cadena_db:str)->bool:  # VALIDAR CADENA DE TEXTO CON HASH GUARDADO
        ...

class BcryptHasher(HasherBase):

    def __init__(self, rounds=12):
        self.rounds = rounds

    def hashear(self, pw):
        salt = bcrypt.gensalt(self.rounds)
        hash_bytes = bcrypt.hashpw(pw.encode("utf-8"),salt)
        return hash_bytes.decode("utf-8")
    
    def verificar(self, pw, pw_db):
        return bcrypt.checkpw(pw.encode("utf-8"),pw_db.encode("utf-8"))
    
hasher: HasherBase = BcryptHasher()

class FlagHasher(HasherBase):
    def hashear(self, flag)->str:
        return hashlib.sha256(flag.encode("utf-8")).hexdigest()
    
    def verificar(self, flag, hash_db)->bool:
        return self.hashear(flag)==hash_db

flag_hasher: HasherBase = FlagHasher()