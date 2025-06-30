from fastapi import HTTPException
from src.models.user_model import User
from argon2 import PasswordHasher
from jose import jwt
from src.utils.config import load_config

config = load_config()
ph = PasswordHasher()


async def register(username: str, password: str):
    if not username or not password:
        raise HTTPException(
            status_code=400, detail="Заполните имя пользователя и пароль"
        )
    existing_user = await User.find_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким именем уже существует"
        )
    hashed_password = ph.hash(password)
    user = await User.create(username, hashed_password)
    user_structure = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }
    token = jwt.encode(
        user_structure, config.get("jwt_secret", "secret"), algorithm="HS256"
    )
    return {"token": token, "user": user_structure}


async def login(username: str, password: str):
    user = await User.find_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    try:
        ph.verify(user["password"], password)
    except:
        raise HTTPException(status_code=401, detail="Неправильный пароль")
    user_structure = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }
    token = jwt.encode(
        claims=user_structure, key=config.get("jwt_secret", "secret"), algorithm="HS256"
    )
    return {"token": token, "user": user_structure}
