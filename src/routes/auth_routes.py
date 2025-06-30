from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.controllers.auth_controller import register, login
from src.middleware.auth_middleware import auth_middleware
from src.utils.config import load_config

router = APIRouter()
config = load_config()
templates = Jinja2Templates(directory="src/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=RedirectResponse)
async def login_route(username: str = Form(...), password: str = Form(...)):
    try:
        result = await login(username, password)
        response = RedirectResponse(url="/products", status_code=303)
        response.set_cookie(key="token", value=result["token"])
        return response
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "login.html", {"request": {}, "error": e.detail}
        )
    except Exception as e:
        print(f"Unexpected error: {e}")  # Для отладки
        return templates.TemplateResponse(
            "login.html", {"request": {}, "error": "Произошла непредвиденная ошибка"}
        )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=RedirectResponse)
async def register_route(username: str = Form(...), password: str = Form(...)):
    try:
        await register(username, password)
        return RedirectResponse(url="/auth/login", status_code=303)
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")  # Для отладки
        return templates.TemplateResponse(
            "register.html", {"request": {}, "error": e.detail}
        )
    except Exception as e:
        print(f"Unexpected error: {e}")  # Для отладки
        return templates.TemplateResponse(
            "register.html", {"request": {}, "error": "Произошла непредвиденная ошибка"}
        )


@router.get("/logout", response_class=RedirectResponse)
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("token")
    return response
