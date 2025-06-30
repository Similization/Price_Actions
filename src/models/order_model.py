from src.utils.db import get_db
import asyncpg


class Order:
    @staticmethod
    async def create(user_id, order_number, account_number=None):
        async with get_db() as conn:
            row = await conn.fetchrow(
                "INSERT INTO orders (user_id, order_number, account_number) VALUES ($1, $2, $3) RETURNING *",
                user_id,
                order_number,
                account_number,
            )
            return (
                dict(
                    zip(
                        [
                            "id",
                            "user_id",
                            "order_number",
                            "account_number",
                            "created_at",
                        ],
                        row,
                    )
                )
                if row
                else None
            )

    @staticmethod
    async def get_by_user(user_id):
        async with get_db() as conn:
            orders = await conn.fetch(
                "SELECT id, order_number, account_number, created_at FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
                user_id,
            )
            result = []
            for order_row in orders:
                order = {
                    "id": order_row[0],
                    "order_number": order_row[1],
                    "account_number": order_row[2],
                    "created_at": order_row[3],
                    "order_products": await OrderItem.get_order_items_by_order_id(
                        order_row[0]
                    ),
                }
                result.append(order)
            return result

    @staticmethod
    async def clear_and_reset():
        async with get_db() as conn:
            await conn.execute("DELETE FROM order_items")
            await conn.execute("DELETE FROM orders")
            await conn.execute("ALTER SEQUENCE orders_id_seq RESTART WITH 1")
            await conn.execute("ALTER SEQUENCE order_items_id_seq RESTART WITH 1")


class OrderItem:
    @staticmethod
    async def get_order_items_by_order_id(order_id):
        async with get_db() as conn:
            rows = await conn.fetch(
                """
                SELECT oi.product_id, oi.quantity, p.name as product_name
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = $1
                """,
                order_id,
            )
            return [
                dict(zip(["product_id", "quantity", "product_name"], row))
                for row in rows
            ]

    @staticmethod
    async def add_item(order_id, product_id, quantity):
        async with get_db() as conn:
            async with conn.transaction():
                await conn.execute(
                    "SELECT quantity FROM products WHERE id = $1 FOR UPDATE", product_id
                )
                product = await conn.fetchrow(
                    "SELECT quantity FROM products WHERE id = $1", product_id
                )
                if not product or product["quantity"] < quantity:
                    raise ValueError("Недостаточно товара на складе")
                try:
                    await conn.execute(
                        "UPDATE products SET quantity = quantity - $1 WHERE id = $2",
                        quantity,
                        product_id,
                    )
                    row = await conn.fetchrow(
                        "INSERT INTO order_items (order_id, product_id, quantity) VALUES ($1, $2, $3) RETURNING *",
                        order_id,
                        product_id,
                        quantity,
                    )
                    return (
                        dict(zip(["id", "order_id", "product_id", "quantity"], row))
                        if row
                        else None
                    )
                except asyncpg.ForeignKeyViolationError:
                    raise ValueError("Неверный идентификатор товара или заказа")
                except Exception as e:
                    raise ValueError(f"Ошибка добавления товара в заказ: {str(e)}")
