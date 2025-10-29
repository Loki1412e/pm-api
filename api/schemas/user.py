from pydantic import BaseModel, constr, conint
from typing import Optional

class UserCreate(BaseModel):
    username: constr(min_length=1, strip_whitespace=True)
    password: constr(min_length=1, strip_whitespace=True)
    ciphertext: constr(min_length=1, strip_whitespace=True)
    iv: constr(min_length=1, strip_whitespace=True)
    salt: constr(min_length=1, strip_whitespace=True)

class UserLogin(BaseModel):
    username: constr(min_length=1, strip_whitespace=True)
    password: constr(min_length=1, strip_whitespace=True)
    jwt_expir: conint(ge=1, le=1440)  # en minutes, entre 1 et 1440 (1min et 24h)

class UserUpdate(BaseModel):
    password: constr(min_length=1, strip_whitespace=True)
    new_username: Optional[constr(min_length=1, strip_whitespace=True)] = None
    new_password: Optional[constr(min_length=1, strip_whitespace=True)] = None

class UserDelete(BaseModel):
    password: constr(min_length=1, strip_whitespace=True)