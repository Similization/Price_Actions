from fastapi import HTTPException
from src.models.product_model import Product
import asyncio


async def get_all():
    return await Product.get_all()


async def update_quantity(product_id: int, quantity: int):
    try:
        product = await Product.update_quantity(product_id, quantity)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def clear_and_reset_products():
    await Product.clear_and_reset()


async def bulk_create_products(csv_data):
    sem = asyncio.Semaphore(5)

    async def process_row(row):
        async with sem:
            name = row.get("name")
            quantity = int(row.get("quantity", 0))
            if name and quantity is not None:
                await Product.create(name, quantity)

    await asyncio.gather(*(process_row(row) for row in csv_data))
