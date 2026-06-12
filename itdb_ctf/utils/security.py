from abc import ABC, abstractclassmethod
import bcrypt

class HasherBase(ABC):

    @abstractclassmethod
    def hashear (self, pw:str)->str:
        ...
    
    @abstractclassmethod
    def verificar(sef, pw:str, pwdb:str)->bool:
        ...

class BcryptHasher(HasherBase):

    def __init__(self, rounds=12):
        self.rounds = rounds

    def hashear(self, pw):
        salt = bcrypt.gensalt(self.rounds)
        hash_bytes = bcrypt.hashpw(pw.encode("utf-8"),salt)
        return hash_bytes.decode("utf-8")
    
    def verificar(sef, pw, pwdb):
        return bcrypt.checkpw(pw.encode("utf-8"),pwdb.encode("utf-8"))
    

hasher: HasherBase = BcryptHasher()