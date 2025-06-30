from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.controllers.reservation_controller import create, update, delete, get_by_user
from src.controllers.product_controller import get_all
from src.middleware.auth_middleware import auth_middleware

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def get_user_reservations(request: Request, user=Depends(auth_middleware)):
    reservations = await get_by_user(user["id"])
    return templates.TemplateResponse(
        "reservations.html",
        {"request": request, "reservations": reservations, "user": user},
    )


@router.post("/create", response_class=RedirectResponse)
async def create_reservation(
    product_id: int = Form(...),
    quantity: int = Form(...),
    user=Depends(auth_middleware),
):
    try:
        await create(user["id"], product_id, quantity)
        return RedirectResponse(url="/reservations", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "products.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        products = await get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": {},
                "products": products,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )


@router.post("/update/{id}", response_class=RedirectResponse)
async def update_reservation(
    id: int, quantity: int = Form(...), user=Depends(auth_middleware)
):
    try:
        await update(id, user["id"], quantity)
        return RedirectResponse(url="/reservations", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "reservations.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        reservations = await get_by_user(user["id"])
        return templates.TemplateResponse(
            "reservations.html",
            {
                "request": {},
                "reservations": reservations,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )


@router.post("/delete/{id}", response_class=RedirectResponse)
async def delete_reservation(id: int, user=Depends(auth_middleware)):
    try:
        await delete(id, user["id"])
        return RedirectResponse(url="/reservations", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "reservations.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        reservations = await get_by_user(user["id"])
        return templates.TemplateResponse(
            "reservations.html",
            {
                "request": {},
                "reservations": reservations,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )
