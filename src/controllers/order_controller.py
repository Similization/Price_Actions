from fastapi import HTTPException
from src.models.order_model import Order, OrderItem
import asyncio


async def create_order(user_id: int, order_number: str, account_number: str = None):
    order = await Order.create(user_id, order_number, account_number)
    if not order:
        raise HTTPException(status_code=400, detail="Не удалось создать заказ")
    return order


async def add_to_order(order_id: int, product_id: int, quantity: int):
    try:
        item = await OrderItem.add_item(order_id, product_id, quantity)
        if not item:
            raise HTTPException(
                status_code=400, detail="Не удалось добавить товар в заказ"
            )
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_user_orders(user_id: int):
    return await Order.get_by_user(user_id)


async def clear_and_reset_orders():
    await Order.clear_and_reset()


async def bulk_create_orders(csv_data):
    sem = asyncio.Semaphore(5)

    async def process_row(row):
        async with sem:
            user_id = int(row.get("user_id", 1))
            order_number = row.get("order_number")
            account_number = row.get("account_number")
            if user_id and order_number:
                await Order.create(user_id, order_number, account_number)

    await asyncio.gather(*(process_row(row) for row in csv_data))
