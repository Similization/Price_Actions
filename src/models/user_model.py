from src.utils.db import get_db
import asyncpg


class User:
    @staticmethod
    async def get_all():
        async with get_db() as conn:
            rows = await conn.fetch("SELECT * FROM users ORDER BY id")
            return [dict(row) for row in rows]

    @staticmethod
    async def find_by_username(username):
        async with get_db() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE username = $1", username
            )
            return dict(row) if row else None

    @staticmethod
    async def find_by_id(user_id):
        async with get_db() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return dict(row) if row else None

    @staticmethod
    async def create(username, password, role="user"):
        async with get_db() as conn:
            try:
                row = await conn.fetchrow(
                    "INSERT INTO users (username, password, role) VALUES ($1, $2, $3) RETURNING *",
                    username,
                    password,
                    role,
                )
                return dict(row)
            except asyncpg.UniqueViolationError:
                raise ValueError("Пользователь с таким именем уже существует")
            except Exception as e:
                raise ValueError(f"Ошибка создания пользователя: {str(e)}")

    @staticmethod
    async def update(user_id, username=None, password=None, role=None):
        async with get_db() as conn:
            query = "UPDATE users SET "
            params = []
            param_index = 1
            if username:
                query += f"username = ${param_index}, "
                params.append(username)
                param_index += 1
            if password:
                query += f"password = ${param_index}, "
                params.append(password)
                param_index += 1
            if role:
                query += f"role = ${param_index}, "
                params.append(role)
                param_index += 1
            query = query.rstrip(", ") + f" WHERE id = ${param_index} RETURNING *"
            params.append(user_id)
            try:
                row = await conn.fetchrow(query, *params)
                return dict(row) if row else None
            except asyncpg.UniqueViolationError:
                raise ValueError("Пользователь с таким именем уже существует")
            except Exception as e:
                raise ValueError(f"Ошибка обновления пользователя: {str(e)}")

    @staticmethod
    async def clear_and_reset():
        async with get_db() as conn:
            await conn.execute("DELETE FROM users")
            await conn.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1")
