from src.utils.db import get_db


class Reservation:
    @staticmethod
    async def create(user_id: int, product_id: int, quantity: int):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(
                    "SELECT quantity FROM products WHERE id = %s FOR UPDATE",
                    (product_id,),
                )
                product = cur.fetchone()
                if not product or product[0] < quantity:
                    raise ValueError("Insufficient stock")
                cur.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                    (quantity, product_id),
                )
                cur.execute(
                    "INSERT INTO reservations (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING *",
                    (user_id, product_id, quantity),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    @staticmethod
    async def update(id: int, user_id: int, quantity: int):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(
                    "SELECT product_id, quantity FROM reservations WHERE id = %s AND user_id = %s",
                    (id, user_id),
                )
                reservation = cur.fetchone()
                if not reservation:
                    raise ValueError("Reservation not found")
                product_id, old_quantity = reservation
                quantity_diff = quantity - old_quantity
                if quantity_diff != 0:
                    cur.execute(
                        "SELECT quantity FROM products WHERE id = %s FOR UPDATE",
                        (product_id,),
                    )
                    product = cur.fetchone()
                    if not product or product[0] < quantity_diff:
                        raise ValueError("Insufficient stock")
                    cur.execute(
                        "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                        (quantity_diff, product_id),
                    )
                cur.execute(
                    "UPDATE reservations SET quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *",
                    (quantity, id),
                )
                result = cur.fetchone()
                conn.commit()
                return result

    @staticmethod
    async def delete(id: int, user_id: int):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(
                    "SELECT product_id, quantity FROM reservations WHERE id = %s AND user_id = %s",
                    (id, user_id),
                )
                reservation = cur.fetchone()
                if not reservation:
                    raise ValueError("Reservation not found")
                product_id, quantity = reservation
                cur.execute(
                    "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                    (quantity, product_id),
                )
                cur.execute("DELETE FROM reservations WHERE id = %s RETURNING *", (id,))
                result = cur.fetchone()
                conn.commit()
                return result

    @staticmethod
    async def get_by_user(user_id: int):
        query = """
            SELECT r.*, p.name as product_name 
            FROM reservations r 
            JOIN products p ON r.product_id = p.id 
            WHERE r.user_id = %s 
            ORDER BY r.created_at DESC
        """
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                return cur.fetchall()
