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
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.payment_methods import Pagamento  # noqa: F401
from settings import LOGGER, Settings

if Settings().SERVER is not None:
    LOGGER.info(
        f"Creating engine to database: {Settings().SERVER=} {Settings().PORT=}"
        f"{Settings().DATABASE=}"
    )
else:
    LOGGER.info(f"Creating engine to database: {Settings().DATABASE=}")

async_engine: AsyncEngine = create_async_engine(
    f"postgresql+asyncpg://{Settings().USER}:{Settings().PASSWORD}@{Settings().SERVER}:{Settings().PORT}/{Settings().DATABASE}"
    if not Settings().RELOAD
    else "sqlite+aiosqlite:///database.db",
    pool_recycle=450,
)
LOGGER.info(f"Engine created: {async_engine=}")


async def get_async_session() -> AsyncGenerator[any, any, AsyncSession]:
    LOGGER.debug(f"Getting async session to {Settings().DATABASE=}")
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


async def create_db_and_tables() -> None:
    LOGGER.info(f"Creating tables to {Settings().DATABASE= }")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    LOGGER.info(f"Tables created to {Settings().DATABASE= }")


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
