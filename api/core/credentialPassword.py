from fastapi import HTTPException
import string
import random

def generateCredentialPassword(length: int = 12, uppercase: bool = True, lowercase: bool = True, digits: bool = True, symbols: bool = True) -> str:
    charset = ""
    if uppercase:
        charset += string.ascii_uppercase
    if lowercase:
        charset += string.ascii_lowercase
    if digits:
        charset += string.digits
    if symbols:
        charset += string.punctuation

    if not charset:
        raise HTTPException(
            status_code=400,
            detail="At least one character type must be selected"
        )

    return ''.join(random.SystemRandom().choice(charset) for _ in range(length))