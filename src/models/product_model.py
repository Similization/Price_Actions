from src.utils.db import get_db
import asyncpg


class Product:
    @staticmethod
    async def get_all():
        async with get_db() as conn:
            rows = await conn.fetch("SELECT * FROM products ORDER BY name")
            return [dict(row) for row in rows]

    @staticmethod
    async def get_by_id(id: int):
        async with get_db() as conn:
            row = await conn.fetch("SELECT * FROM products WHERE id = $1", id)
            return dict(row[0]) if row else None

    @staticmethod
    async def create(name, quantity):
        async with get_db() as conn:
            row = await conn.fetchrow(
                "INSERT INTO products (name, quantity) VALUES ($1, $2) RETURNING *",
                name,
                quantity,
            )
            return dict(row)

    @staticmethod
    async def update_quantity(product_id, quantity):
        async with get_db() as conn:
            try:
                row = await conn.fetchrow(
                    "UPDATE products SET quantity = quantity + $1 WHERE id = $2 RETURNING *",
                    quantity,
                    product_id,
                )
                return dict(row) if row else None
            except asyncpg.ForeignKeyViolationError:
                raise ValueError("Товар с указанным ID не найден")
            except Exception as e:
                raise ValueError(f"Ошибка обновления количества: {str(e)}")

    @staticmethod
    async def clear_and_reset():
        async with get_db() as conn:
            await conn.execute("DELETE FROM products")
            await conn.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1")
