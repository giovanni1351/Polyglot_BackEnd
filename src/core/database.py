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

from astrapy import AsyncDatabase, DataAPIClient
from beanie import init_beanie  # type: ignore
from fastapi import Depends
from pymongo import AsyncMongoClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.compras import criar_compras
from schemas.payment_methods import Pagamento  # type: ignore # noqa: F401
from schemas.products import Product
from settings import SETTINGS

async_engine: AsyncEngine = create_async_engine(
    f"postgresql+asyncpg://{SETTINGS.DB_USER}:{SETTINGS.PASSWORD}@{SETTINGS.SERVER}:{SETTINGS.PORT}/{SETTINGS.DATABASE}"
    if not SETTINGS.RELOAD
    else "sqlite+aiosqlite:///database.db",
    poolclass=NullPool,  # Para ambientes serverless
    connect_args={
        # Desabilita JIT do PostgreSQL para melhor performance em serverless
        "server_settings": {"jit": "off"},
        "command_timeout": 60,
        "timeout": 30,
    }
    if not SETTINGS.RELOAD
    else {},
)

Cassandra_db: AsyncDatabase | None = None


async def get_async_session() -> AsyncGenerator[Any, AsyncSession]:
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


async def get_cassandra_session() -> AsyncGenerator[Any, AsyncDatabase]:
    client = DataAPIClient(
        SETTINGS.ASTRA_TOKEN if SETTINGS.ASTRA_TOKEN is not None else ""
    )
    yield client.get_async_database_by_api_endpoint(
        SETTINGS.ASTRA_ENDPOINT if SETTINGS.ASTRA_ENDPOINT is not None else "",
        keyspace="Polyglot",
    )


async def create_db_and_tables() -> None:
    client = AsyncMongoClient(  # type: ignore
        "mongodb+srv://mongo:mongo@6o-semedtre.fpkb99x.mongodb.net/"
        "?retryWrites=true&w=majority&appName=6o-semedtre"
    )
    await init_beanie(database=client.projeto, document_models=[Product])  # type: ignore

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
CassandraSessionDep = Annotated[AsyncDatabase, Depends(get_cassandra_session)]


async def init_astra_cassandra() -> None:
    global Cassandra_db
    # Initialize the client
    client = DataAPIClient(
        SETTINGS.ASTRA_TOKEN if SETTINGS.ASTRA_TOKEN is not None else ""
    )
    Cassandra_db = client.get_async_database_by_api_endpoint(
        SETTINGS.ASTRA_ENDPOINT if SETTINGS.ASTRA_ENDPOINT is not None else "",
        keyspace="Polyglot",
    )

    print("Connected to Astra DB", Cassandra_db)
    Cassandra_db.get_collection("compras")
    await criar_compras(Cassandra_db)
