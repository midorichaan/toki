from dotenv import load_dotenv
from functools import wraps
from typing import Coroutine

import aiomysql
import os

load_dotenv()

class Database:
    def __init__(
        self, *, host: str = os.environ.get("DB_HOST", None), port: int = os.environ.get("DB_PORT", 3306),
            user: str = os.environ.get("DB_USER", None), password: str = os.environ.get("DB_PASSWD", None), db: str = os.environ.get("DB_DATABASE", None)
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.db: str = db
        self.pool: aiomysql.Pool = None

    async def setup(self) -> aiomysql.Pool:
        self.pool = await aiomysql.create_pool(
            host=self.host, port=self.port,
            user=self.user, password=self.password, db=self.db,
            autocommit=True, cursorclass=aiomysql.cursors.DictCursor
        )
        return self.pool

    def check_connection(func) -> Coroutine:
        @wraps(func)
        async def inner(self, *args, **kwargs):
            self.pool = self.pool or await self.setup()
            return await func(self, *args, **kwargs)
        return inner
    
    @check_connection
    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()

    @check_connection
    async def execute(self, sql: str, *args, **kwargs) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, *args, **kwargs)

    @check_connection
    async def fetchall(self, sql: str = None, *args, **kwargs) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if sql is not None:
                    await cur.execute(sql, *args, **kwargs)
                return await cur.fetchall()
    
    @check_connection
    async def executemany(self, sql: str = None, *args, **kwargs) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(sql, *args, **kwargs)

    @check_connection
    async def fetchone(self, sql: str = None, *args, **kwargs) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if sql is not None:
                    await cur.execute(sql, *args, **kwargs)
                return await cur.fetchone()
