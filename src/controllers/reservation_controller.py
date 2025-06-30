from fastapi import HTTPException
from src.models.reservation_model import Reservation


async def create(user_id: int, product_id: int, quantity: int):
    if not product_id or quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid product ID or quantity")
    try:
        reservation = await Reservation.create(user_id, product_id, quantity)
        return reservation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update(id: int, user_id: int, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    try:
        reservation = await Reservation.update(id, user_id, quantity)
        return reservation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def delete(id: int, user_id: int):
    try:
        reservation = await Reservation.delete(id, user_id)
        return reservation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_by_user(user_id: int):
    reservations = await Reservation.get_by_user(user_id)
    return reservations
