import asyncpg
from contextlib import asynccontextmanager
from src.utils.config import load_config

config = load_config()


async def get_db_connection():
    print(config.get("db_user", "postgres"))
    print(config.get("db_host", "localhost"))
    print(config.get("db_name", "inventory"))
    print(config.get("db_password", "password"))
    print(config.get("db_port", 5432))
    try:
        conn = await asyncpg.connect(
            user=config.get("db_user", "postgres"),
            host=config.get("db_host", "localhost"),
            database=config.get("db_name", "inventory"),
            password=config.get("db_password", "password"),
            port=config.get("db_port", 5432),
        )
    except Exception as e:
        print(e)

    return conn


@asynccontextmanager
async def get_db():
    conn = await get_db_connection()
    print(conn)
    try:
        async with conn.transaction():
            yield conn
    except Exception as e:
        raise e
    finally:
        await conn.close()
