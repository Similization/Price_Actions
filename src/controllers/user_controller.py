from fastapi import HTTPException
from src.models.user_model import User
from src.models.order_model import Order
from argon2 import PasswordHasher
from jose import jwt
from src.utils.config import load_config
import asyncio

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
    user = await User.create(username, hashed_password, "user")
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
    if not ph.verify(user["password"], password):
        raise HTTPException(status_code=401, detail="Неправильный пароль")
    user_structure = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }
    token = jwt.encode(
        user_structure, config.get("jwt_secret", "secret"), algorithm="HS256"
    )
    return {"token": token, "user": user_structure}


async def get_all_users():
    return await User.get_all()


async def create_user(username: str, password: str, role: str = "user"):
    if not username or not password:
        raise HTTPException(
            status_code=400, detail="Заполните имя пользователя и пароль"
        )
    hashed_password = ph.hash(password)
    return await User.create(username, hashed_password, role)


async def update_user(
    user_id: int, username: str = None, password: str = None, role: str = None
):
    if not username and not password and not role:
        raise HTTPException(
            status_code=400, detail="Укажите хотя бы одно поле для обновления"
        )
    hashed_password = ph.hash(password) if password else None
    user = await User.update(user_id, username, hashed_password, role)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


async def get_user_details(user_id: int):
    user = await User.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    orders = await Order.get_by_user(user_id)
    return {"user": user, "orders": orders}


async def clear_and_reset_users():
    await User.clear_and_reset()


async def bulk_create_users(csv_data):
    sem = asyncio.Semaphore(5)

    async def process_row(row):
        async with sem:
            username = row.get("username")
            password = row.get("password")
            role = row.get("role", "user")
            if username and password:
                hashed_password = ph.hash(password)
                await User.create(username, hashed_password, role)

    await asyncio.gather(*(process_row(row) for row in csv_data))
