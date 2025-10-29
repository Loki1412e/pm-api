from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.credential import Credential
from typing import Optional

async def create_credential(domain: str, username: str, ciphertext: str, iv: str, description: str, user_id: int, db: AsyncSession) -> bool:
    cred = Credential(domain=domain, username=username, ciphertext=ciphertext, iv=iv, description=description, user_id=user_id)
    db.add(cred)
    try:
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print(f"Erreur create_credential: {e}")
        return False

async def get_credentials_by_user_id(user_id: int, domain: Optional[str], username: Optional[str], description: Optional[str], db: AsyncSession):
    query = select(Credential).where(Credential.user_id == user_id)

    if domain:
        query = query.where(Credential.domain.ilike(f"%{domain}%"))
    if username:
        query = query.where(Credential.username.ilike(f"%{username}%"))
    if description:
        query = query.where(Credential.description.ilike(f"%{description}%"))

    result = await db.execute(query)
    return result.scalars().all()

async def get_credential_by_id(credential_id: int, db: AsyncSession):
    result = await db.execute(select(Credential).where(Credential.id == credential_id))
    return result.scalars().first()

async def get_credential_by_id_and_user_id(credential_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Credential).where(Credential.id == credential_id, Credential.user_id == user_id)
    )
    return result.scalars().first()

async def update_credential(credential_id: int, domain: str, username: str, ciphertext: str, iv: str, description: str, db: AsyncSession) -> bool:
    stmt = (
        update(Credential)
        .where(Credential.id == credential_id)
        .values(domain=domain, username=username, ciphertext=ciphertext, iv=iv, description=description)
        .execution_options(synchronize_session="fetch")
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        print(f"Erreur update_credential: {e}")
        return False

async def delete_credential(credential_id: int, db: AsyncSession) -> bool:
    stmt = delete(Credential).where(Credential.id == credential_id)
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        print(f"Erreur delete_credential: {e}")
        return False
