from pydantic import BaseModel, constr
from typing import Optional

class CredentialCreate(BaseModel):
    domain: constr(min_length=1, strip_whitespace=True)
    username: constr(min_length=1, strip_whitespace=True)
    ciphertext: constr(min_length=1, strip_whitespace=True)
    iv: constr(min_length=1, strip_whitespace=True)
    description: Optional[constr(min_length=1, strip_whitespace=True)] = None

class CredentialUpdate(BaseModel):
    new_site: Optional[constr(min_length=1, strip_whitespace=True)] = None
    new_username: Optional[constr(min_length=1, strip_whitespace=True)] = None
    new_ciphertext: Optional[constr(min_length=1, strip_whitespace=True)] = None
    new_description: Optional[constr(min_length=1, strip_whitespace=True)] = None

class CredentialOut(BaseModel):
    id: int
    domain: constr(min_length=1, strip_whitespace=True)
    username: constr(min_length=1, strip_whitespace=True)
    ciphertext: Optional[constr(min_length=1, strip_whitespace=True)] = None
    iv: Optional[constr(min_length=1, strip_whitespace=True)] = None
    description: Optional[constr(min_length=1, strip_whitespace=True)] = None
    user_id: int

    class Config:
        from_attributes = True