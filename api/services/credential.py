from dao import credential as dao_credential
from dao.user import get_user_by_id
from core.hashing import verify_password
from typing import Optional

async def create(domain: str, username: str, ciphertext: str, iv: str, salt: str, description: str, user_id: int, db) -> dict:
    """
    Création d'un credential.
    ciphertext : ciphertext côté client
    iv : IV utilisé pour AES-GCM (base64)
    salt : salt pour dérivation de clé (base64)
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        return {"status": 404, "message": "User not found"}

    created = await dao_credential.create_credential(domain, username, ciphertext, iv, salt, description, user_id, db)
    if created:
        return {"status": 201, "message": "Credential created successfully"}
    return {"status": 500, "message": "Failed to create credential"}


async def get_credentials_by_user_id(user_id: int, domain: Optional[str], username: Optional[str], description: Optional[str], db) -> dict:
    user = await get_user_by_id(user_id, db)
    if not user:
        return {"status": 404, "message": "User not found"}
    
    rows = await dao_credential.get_credentials_by_user_id(user_id, domain, username, description, db)
    credentials = [
        {
            "id": c.id,
            "domain": c.domain,
            "username": c.username,
            "password": c.ciphertext and c.iv, # Indique si le mot de passe peut être déchiffré
            "description": c.description,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in rows
    ]

    return {"status": 200, "message": "Credentials fetched successfully", "credentials": credentials}


async def get_credential_by_id_and_user_id(credential_id: int, user_id: int, db) -> dict:
    credential = await dao_credential.get_credential_by_id_and_user_id(credential_id, user_id, db)
    if not credential:
        return {"status": 404, "message": "Credential not found"}

    return {
        "status": 200,
        "message": "Credential fetched successfully",
        "data": {
            "id": credential.id,
            "domain": credential.domain,
            "username": credential.username,
            "ciphertext": credential.ciphertext,
            "iv": credential.iv,
            "description": credential.description
        }
    }


async def update(credential_id: int, user_id: int, new_site: str = None, new_username: str = None, new_ciphertext: str = None, new_description: str = None, db=None) -> dict:
    """
    Mise à jour d'un credential.
    Le mot de passe doit être déjà chiffré côté client.
    """
    credential = await dao_credential.get_credential_by_id_and_user_id(credential_id, user_id, db)
    if not credential:
        return {"status": 404, "message": "Credential not found"}

    new_site = credential.domain if new_site is None else new_site
    new_username = credential.username if new_username is None else new_username
    new_ciphertext = credential.ciphertext if new_ciphertext is None else new_ciphertext
    new_description = credential.description if new_description is None else new_description

    updated = await dao_credential.update_credential(credential_id, new_site, new_username, new_ciphertext, new_description, db)
    if updated:
        return {"status": 200, "message": "Credential updated successfully"}
    return {"status": 500, "message": "Failed to update credential"}


async def delete(credential_id: int, user_id: int, db) -> dict:
    credential = await dao_credential.get_credential_by_id(credential_id, db)
    if not credential:
        return {"status": 404, "message": "Credential not found"}

    if credential.user_id != user_id:
        return {"status": 403, "message": "Access forbidden"}

    deleted = await dao_credential.delete_credential(credential_id, db)
    if deleted:
        return {"status": 200, "message": "Credential deleted successfully"}
    return {"status": 500, "message": "Failed to delete credential"}
