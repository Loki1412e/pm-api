from dao import user as dao_user
from dao.credential import get_credentials_by_user_id, create_credential
from core.hashing import hash_password, verify_password
from core.jwt import generate_jwt


async def create(user, db) -> dict:
    existing_user = await dao_user.get_user_by_username(user.username, db)
    if existing_user:
        return {"status": 401, "message": "Username already exists"}

    # Renvoie l'ID de l'utilisateur
    new_user = await dao_user.create_user(user.username, hash_password(user.password), db)
    if not new_user:
        return {"status": 500, "message": "Failed to create user"}

    # passwd == 'PM:<username>'
    verificationCredential = await create_credential(
        "password-manager",
        user.username,
        user.ciphertext,
        user.iv,
        user.salt,
        "Verification Master Password",
        new_user.id,
        db
    )
    if not verificationCredential:
        await dao_user.delete_user(new_user.id, db)
        return {"status": 500, "message": "Failed to create user credential, user deleted"}

    return {"status": 201, "message": "User created successfully"}


async def login(username: str, password: str, jwt_expir: int, db) -> dict:
    user = await dao_user.get_user_by_username(username, db)
    if not user or not verify_password(password, user.password):
        return {"status": 401, "message": "Invalid credentials"}
    
    token = generate_jwt({"id": user.id, "username": user.username}, jwt_expir)
    
    rows = await get_credentials_by_user_id(user.id, None, None, None, db)
    credentials = [
        {
            "id": c.id,
            "domain": c.domain,
            "username": c.username,
            "ciphertext": c.ciphertext,
            "iv": c.iv,
            "salt": c.salt,
            "description": c.description,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in rows
    ]

    return {"status": 200, "message": "Login successful", "token": token, "credentials": credentials}


async def count(db) -> dict:
    count = await dao_user.get_count_of_user(db)
    return {"status": 200, "message": "Users counted successfully", "count": count}


# async def get_all_users_id(db) -> dict:
#     rows = await dao_user.get_all_users_id(db)
#     # users = [dict(id=row.id, username=row.username) for row in rows]
#     return {"status": 200, "message": "Users fetched successfully", "users": rows}


async def read(user_id: int, db) -> dict:
    user = await dao_user.get_user_by_id(user_id, db)
    if not user:
        return {"status": 404, "message": "User not found"}
    return {"status": 200, "message": "User fetched successfully", "user": dict(id=user.id, username=user.username)}


async def update(user_id: int, password: str, new_username: str = None, new_password: str = None, db=None) -> dict:
    user = await dao_user.get_user_by_id(user_id, db)
    if not user:
        return {"status": 404, "message": "User not found"}

    if not verify_password(password, user.password):
        return {"status": 401, "message": "Invalid credentials"}

    if new_username:
        existing_user = await dao_user.get_user_by_username(new_username, db)
        if existing_user and existing_user.id != user_id:
            return {"status": 401, "message": "Username already exists"}

    new_username = user.username if not new_username else new_username
    new_password_hashed = user.password if not new_password else hash_password(new_password)

    updated = await dao_user.update_user(user_id, new_username, new_password_hashed, db)
    if updated:
        return {"status": 200, "message": "User updated successfully", "token": generate_jwt({"id": user_id, "username": new_username})}

    return {"status": 500, "message": "Failed to update user"}


async def delete(user_id: int, password: str, db) -> dict:
    user = await dao_user.get_user_by_id(user_id, db)
    if not user:
        return {"status": 404, "message": "User not found"}

    if not verify_password(password, user.password):
        return {"status": 401, "message": "Invalid credentials"}

    deleted = await dao_user.delete_user(user_id, db)
    if deleted:
        return {"status": 200, "message": "User deleted successfully"}
    return {"status": 500, "message": "Failed to delete user"}
