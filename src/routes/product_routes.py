from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.controllers.product_controller import get_all, update_quantity
from src.middleware.auth_middleware import auth_middleware

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def get_all_products(
    request: Request, search: str = None, user=Depends(auth_middleware)
):
    products = await get_all()
    cart = request.session.get("cart", {"products": []})
    if not isinstance(cart, dict) or not isinstance(cart.get("products"), list):
        cart = {"products": []}
        request.session["cart"] = cart
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    adjusted_products = [
        (
            p["id"],
            p["name"],
            max(
                0,
                p["quantity"]
                - sum(
                    i["quantity"]
                    for i in cart["products"]
                    if i["product_id"] == p["id"]
                ),
            ),
            p["created_at"],
        )
        for p in products
    ]
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": adjusted_products, "user": user, "cart": cart},
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, user=Depends(auth_middleware)):
    if user["role"] != "admin":
        return templates.TemplateResponse(
            "products.html",
            {"request": request, "error": "Админ-доступ требуется", "user": user},
        )
    products = await get_all()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "products": products, "user": user}
    )


@router.post("/update/{id}", response_class=RedirectResponse)
async def update_product_quantity(
    id: int, quantity: int = Form(...), user=Depends(auth_middleware)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/products", status_code=303)
    try:
        await update_quantity(id, quantity)
        return RedirectResponse(url="/products/admin", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "admin.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        products = await get_all()
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": {},
                "products": products,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )
