from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.credential import CredentialCreate, CredentialUpdate
from services import credential as credentials_service
from core.jwt import jwt_required
from core.logging import logger # ex: logger.info("User created successfully")

router = APIRouter(prefix="/credentials", tags=["credentials"])

@router.put("/create", response_model=dict)
async def create_credential(credential: CredentialCreate, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    result = await credentials_service.create(
        domain=credential.domain,
        username=credential.username,
        ciphertext=credential.ciphertext,
        iv=credential.iv,
        description=credential.description,
        user_id=userJWT["user_id"],
        db=db
    )
    if result["status"] != 201:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.get("/list", response_model=dict)
async def get_credentials_by_user_id(
    domain: Optional[str] = Query(default="", description="Nom du domain"),
    username: Optional[str] = Query(default="", description="Nom d'utilisateur"),
    description: Optional[str] = Query(default="", description="Description"),
    userJWT=Depends(jwt_required),
    db: AsyncSession = Depends(get_db)
):
    result = await credentials_service.get_credentials_by_user_id(userJWT["user_id"], domain, username, description, db)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.get("/read/{credential_id}", response_model=dict)
async def read_credential(credential_id: int, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    """
    Retourne ciphertext, iv et salt pour que le client puisse déchiffrer localement
    """
    result = await credentials_service.get_credential_by_id_and_user_id(credential_id, userJWT["user_id"], db)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.patch("/update/{credential_id}", response_model=dict)
async def update_credential(credential_id: int, credential: CredentialUpdate, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    """
    Met à jour un credential. Le password doit être déjà chiffré côté client si modifié (= ciphertext).
    """
    result = await credentials_service.update(
        credential_id=credential_id,
        user_id=userJWT["user_id"],
        new_site=credential.new_site,
        new_username=credential.new_username,
        new_ciphertext=credential.new_ciphertext,
        new_description=credential.new_description,
        db=db
    )
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.delete("/delete/{credential_id}", response_model=dict)
async def delete_credential(credential_id: int, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    result = await credentials_service.delete(credential_id, userJWT["user_id"], db)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result
