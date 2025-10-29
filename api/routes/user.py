from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.user import UserCreate, UserLogin, UserUpdate, UserDelete
from services import user as user_service
from core.jwt import jwt_required
from core.logging import logger # ex: logger.info("User created successfully")

router = APIRouter(prefix="/user", tags=["Users"])

@router.put("/create", response_model=dict)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await user_service.create(user, db)
    if result["status"] != 201:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.post("/login", response_model=dict)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login. Renvoie un JWT pour authentification + Master Salt + Credentials (Vault)
    """
    result = await user_service.login(user.username, user.password, user.jwt_expir, db)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.get("/count", response_model=dict)
async def count_users(db: AsyncSession = Depends(get_db)):
    return await user_service.count(db)

@router.get("/read", response_model=dict)
async def read_user(userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    return await user_service.read(userJWT["user_id"], db)

@router.patch("/update", response_model=dict)
async def update_user(user: UserUpdate, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    result = await user_service.update(
        user_id=userJWT["user_id"],
        current_password=user.password,
        new_username=user.new_username,
        new_password=user.new_password,
        db=db
    )
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

@router.delete("/delete", response_model=dict)
async def delete_user(user: UserDelete, userJWT=Depends(jwt_required), db: AsyncSession = Depends(get_db)):
    result = await user_service.delete(userJWT["user_id"], user.password, db)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result