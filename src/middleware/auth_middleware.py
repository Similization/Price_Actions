from fastapi import HTTPException, Request
from jose import jwt, JWTError
from src.utils.config import load_config

config = load_config()


async def auth_middleware(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(
            token, config.get("jwt_secret", "secret"), algorithms=["HS256"]
        )
        request.state.user = payload
        print(payload)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
