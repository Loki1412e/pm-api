from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

async def get_user_by_username(username: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(username: str, password_hash: str, db: AsyncSession) -> bool:
    user = User(username=username, password=password_hash)
    db.add(user)
    try:
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print(f"Erreur create_user: {e}")
        return False

# async def get_all_users_id(db: AsyncSession):
#     result = await db.execute(select(User.id))
#     return result.scalars().all()

async def get_count_of_user(db: AsyncSession):
    result = await db.execute(select(func.count(User.id)))
    return result.scalar() or 0

async def update_user(user_id: int, new_username: str, new_password: str, db: AsyncSession) -> bool:
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(username=new_username, password=new_password)
        .execution_options(synchronize_session="fetch")
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        print(f"Erreur update_user: {e}")
        return False

async def delete_user(user_id: int, db: AsyncSession) -> bool:
    stmt = delete(User).where(User.id == user_id)
    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        print(f"Erreur delete_user: {e}")
        return False
