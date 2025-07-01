from fastapi import APIRouter, HTTPException, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.controllers.user_controller import (
    get_all_users,
    create_user,
    update_user,
    get_user_details
)
from src.controllers.product_controller import (
    clear_and_reset_products,
    bulk_create_products,
)
from src.controllers.product_controller import clear_and_reset_products, get_all
from src.controllers.order_controller import clear_and_reset_orders
from src.middleware.auth_middleware import auth_middleware
from src.utils.data_changer import calculate_product_count

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def get_users_panel(request: Request, user=Depends(auth_middleware)):
    if user["role"] != "admin":
        return templates.TemplateResponse(
            "products.html",
            {"request": request, "error": "Админ-доступ требуется", "user": user},
        )
    users = await get_all_users()
    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users, "user": user}
    )


@router.post("/create", response_class=RedirectResponse)
async def create_user_route(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    user=Depends(auth_middleware),
):
    if user["role"] != "admin":
        return RedirectResponse(url="/products", status_code=303)
    try:
        await create_user(username, password, role)
        return RedirectResponse(url="/users", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "users.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        users = await get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {
                "request": {},
                "users": users,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )


@router.post("/update/{id}", response_class=RedirectResponse)
async def update_user_route(
    id: int,
    username: str = Form(None),
    password: str = Form(None),
    role: str = Form(None),
    user=Depends(auth_middleware),
):
    if user["role"] != "admin":
        return RedirectResponse(url="/products", status_code=303)
    try:
        await update_user(id, username, password, role)
        return RedirectResponse(url="/users", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "users.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        users = await get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {
                "request": {},
                "users": users,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )


@router.get("/{id}/details", response_class=HTMLResponse)
async def get_user_details_route(
    request: Request, id: int, user=Depends(auth_middleware)
):
    if user["role"] != "admin":
        return templates.TemplateResponse(
            "products.html",
            {"request": request, "error": "Админ-доступ требуется", "user": user},
        )
    try:
        details = await get_user_details(id)
        products = calculate_product_count(orders=details["orders"])
        cart = request.session.get(f"cart_{id}", {"products": []})
        if not isinstance(cart.get("products"), list):
            cart = {"products": []}
        return templates.TemplateResponse(
            "user_details.html",
            {
                "request": request,
                "user_details": details["user"],
                "orders": details["orders"],
                "products": products,
                "cart": cart,
                "user": user,
            },
        )
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "users.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        users = await get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {
                "request": {},
                "users": users,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )


@router.get("/upload", response_class=HTMLResponse)
async def get_upload_page(request: Request, user=Depends(auth_middleware)):
    if user["role"] != "admin":
        return templates.TemplateResponse(
            "products.html",
            {"request": request, "error": "Админ-доступ требуется", "user": user},
        )
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@router.post("/upload", response_class=RedirectResponse)
async def upload_file(
    request: Request, file: UploadFile = File(...), user=Depends(auth_middleware)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/products", status_code=303)
    try:
        if not file.filename.endswith(".txt"):
            raise ValueError("Пожалуйста, загрузите файл с расширением .txt")
        content = await file.read()
        lines = content.decode("utf-8").splitlines()
        products_data = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    name, quantity = line.split(",")
                    products_data.append(
                        {"name": name.strip(), "quantity": int(quantity.strip())}
                    )
                except ValueError as e:
                    raise ValueError(
                        f"Неверный формат строки: {line}. Ожидается 'название,количество'"
                    )
        # Очистка order_items перед загрузкой продуктов

        await clear_and_reset_orders()
        await clear_and_reset_products()

        # Загрузка продуктов
        if products_data:
            await bulk_create_products(products_data)
        return RedirectResponse(url="/products", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "products.html", {"request": {}, "error": e.detail, "user": user}
        )
    except Exception as e:
        products = await get_all()  # Предполагаемый метод
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "products": products,
                "error": "Произошла непредвиденная ошибка",
                "user": user,
            },
        )
