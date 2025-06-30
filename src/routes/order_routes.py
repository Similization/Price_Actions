from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.controllers.order_controller import create_order, add_to_order, get_user_orders
from src.middleware.auth_middleware import auth_middleware
from src.models.product_model import Product

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.post("/add", response_class=RedirectResponse)
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    user=Depends(auth_middleware),
):
    if user["role"] == "admin":
        products = await Product.get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "error": "Администраторы не могут добавлять товары в корзину",
                "user": user,
                "products": products,
                "cart": {"products": []},
            },
        )
    cart = request.session.get("cart", {"products": []})
    if not isinstance(cart.get("products"), list):
        cart["products"] = []
    for item in cart["products"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        product = await Product.get_by_id(product_id)
        cart["products"].append(
            {
                "product_id": product_id,
                "quantity": quantity,
                "product_name": product["name"],
            }
        )
    request.session["cart"] = cart
    return RedirectResponse(url="/products", status_code=303)


@router.post("/create", response_class=RedirectResponse)
async def create_order_route(
    request: Request,
    order_number: str = Form(...),
    account_number: str = Form(None),
    user=Depends(auth_middleware),
):
    if user["role"] == "admin":
        products = await Product.get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "error": "Администраторы не могут формировать заказы",
                "user": user,
                "products": products,
                "cart": {"products": []},
            },
        )
    cart = request.session.get("cart", {"products": []})
    if not cart["products"]:
        products = await Product.get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "error": "Заказ пуст",
                "user": user,
                "products": products,
                "cart": cart,
            },
        )
    order = await create_order(user["id"], order_number, account_number)
    for item in cart["products"]:
        await add_to_order(order["id"], item["product_id"], item["quantity"])
    request.session["cart"] = {"products": []}
    return RedirectResponse(url="/products", status_code=303)


@router.get("/clear", response_class=RedirectResponse)
async def clear_cart(request: Request, user=Depends(auth_middleware)):
    if user["role"] == "admin":
        products = await Product.get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "error": "Администраторы не могут очищать корзину",
                "user": user,
                "products": products,
                "cart": {"products": []},
            },
        )
    request.session["cart"] = {"products": []}
    return RedirectResponse(url="/products", status_code=303)


@router.post("/remove", response_class=RedirectResponse)
async def remove_from_cart(
    request: Request, product_id: int = Form(...), user=Depends(auth_middleware)
):
    if user["role"] == "admin":
        products = await Product.get_all()
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "error": "Администраторы не могут удалять товары из корзины",
                "user": user,
                "products": products,
                "cart": {"products": []},
            },
        )
    cart = request.session.get("cart", {"products": []})
    if not isinstance(cart.get("products"), list):
        cart["products"] = []
    for item in cart["products"]:
        if item["product_id"] == product_id:
            cart["products"].remove(item)
            break
    request.session["cart"] = cart
    return RedirectResponse(url="/products", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def get_orders(request: Request, user=Depends(auth_middleware)):
    orders = await get_user_orders(user["id"])
    return templates.TemplateResponse(
        "orders.html", {"request": request, "orders": orders, "user": user}
    )
