import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.b64encode(salt + key).decode()

def verify_password(password: str, hashed: str) -> bool:
    decoded = base64.b64decode(hashed.encode())
    salt = decoded[:16]
    key = decoded[16:]
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    try:
        kdf.verify(password.encode(), key)
        return True
    except InvalidKey:
        return False