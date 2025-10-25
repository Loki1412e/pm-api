from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db, engine, wait_for_db
from sqlalchemy.exc import SQLAlchemyError
from core.config import TRAEFIK_PATH_PREFIX
from core.credentialPassword import generateCredentialPassword
from core.logging import logger # ex: logger.info("User created successfully")

router = APIRouter(prefix="/utils", tags=["Utils"])

@router.get("/generatePassword", response_model=dict)
async def generate_password(
    length: Optional[int] = 16,
    uppercase: Optional[bool] = True,
    lowercase: Optional[bool] = True,
    digits: Optional[bool] = True,
    symbols: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
):
    password = generateCredentialPassword(length, uppercase, lowercase, digits, symbols)
    return {
        "status": 200,
        "data": {
            "password": password,
            "length": length,
            "uppercase": uppercase,
            "lowercase": lowercase,
            "digits": digits,
            "symbols": symbols
        },
        "message": "Password generated successfully"
    }

@router.get("/healthcheck", response_model=dict)
async def healthcheck(db: AsyncSession = Depends(get_db)):
    """
    Vérifie que l'API et la DB sont opérationnelles.
    """
    db_status = True
    db_error = None
    try:
        # Teste la DB via wait_for_db, 1 essai suffisant
        await wait_for_db(engine, retries=1, delay=0)
    except SQLAlchemyError as e:
        db_status = False
        db_error = str(e)
    except RuntimeError as e:
        db_status = False
        db_error = str(e)

    return {
        "status": 200 if db_status else 500,
        "data": {
            "api": "running",
            "db_status": db_status,
            "db_error": db_error
        }
    }
