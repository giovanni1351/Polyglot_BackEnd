"""
# Exemplo de como adicionar um modelo utilizando o SQLModel
```python
from database import SessionDep, engine

with SessionDep(engine) as session:
    session.add(modelo)
    session.commit()
    session.refresh(modelo)
```

"""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from beanie import init_beanie  # type: ignore
from fastapi import Depends
from pymongo import AsyncMongoClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.payment_methods import Pagamento  # type: ignore # noqa: F401
from schemas.products import Product
from settings import LOGGER, SETTINGS

if SETTINGS.SERVER is not None:
    LOGGER.info(
        f"Creating engine to database: {SETTINGS.SERVER=} {SETTINGS.PORT=}"
        f"{SETTINGS.DATABASE=}"
    )
else:
    LOGGER.info(f"Creating engine to database: {SETTINGS.DATABASE=}")

async_engine: AsyncEngine = create_async_engine(
    f"postgresql+asyncpg://{SETTINGS.DB_USER}:{SETTINGS.PASSWORD}@{SETTINGS.SERVER}:{SETTINGS.PORT}/{SETTINGS.DATABASE}"
    if not SETTINGS.RELOAD
    else "sqlite+aiosqlite:///database.db",
    pool_recycle=450,
)
LOGGER.info(f"Engine created: {async_engine=}")


async def get_async_session() -> AsyncGenerator[Any, AsyncSession]:
    LOGGER.debug(f"Getting async session to {SETTINGS.DATABASE=}")
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


async def create_db_and_tables() -> None:
    client = AsyncMongoClient(  # type: ignore
        "mongodb+srv://mongo:mongo@6o-semedtre.fpkb99x.mongodb.net/"
        "?retryWrites=true&w=majority&appName=6o-semedtre"
    )
    await init_beanie(database=client.projeto, document_models=[Product])  # type: ignore
    LOGGER.info(f"Creating tables to {SETTINGS.DATABASE= }")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    LOGGER.info(f"Tables created to {SETTINGS.DATABASE= }")


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


# # Initialize the client
# client = DataAPIClient(SETTINGS.ASTRA_TOKEN)  # pyright: ignore[reportArgumentType]
# db = client.get_database_by_api_endpoint(SETTINGS.ASTRA_ENDPOINT, keyspace="Polyglot")  # pyright: ignore[reportArgumentType]

# print(f"Connected to Astra DB: {db.list_collection_names()}")
