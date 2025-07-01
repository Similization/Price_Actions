import sys
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from src.routes import auth_routes, product_routes, user_routes, order_routes
from src.utils.config import load_config
import uvicorn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = load_config()

app = FastAPI()

# Подключение сессий
app.add_middleware(SessionMiddleware, secret_key=config.get("jwt_secret", "secret"))

# Подключение статических файлов (CSS)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(product_routes.router, prefix="/products")
app.include_router(user_routes.router, prefix="/users")
app.include_router(order_routes.router, prefix="/orders")

@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login")  # Перенаправляем на /docs

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=config.get("port", 8000))
