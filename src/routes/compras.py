import datetime
from collections.abc import Iterable
from typing import Annotated

from fastapi import APIRouter, Depends

from core.auth import get_current_user
from core.database import CassandraSessionDep
from schemas.compras import Compras
from schemas.user import User

router = APIRouter(prefix="/compras", tags=["vendas"])


@router.post("/")
async def create_compra(
    compra: Compras,
    current_user: Annotated[User, Depends(get_current_user)],
    cassandra_db: CassandraSessionDep,
) -> Compras:
    tabela = cassandra_db.get_table("compras")
    resultado = await tabela.insert_one(compra.model_dump())
    print(resultado)
    return compra


@router.get("/{user_id}")
async def get_compras(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    cassandra_db: CassandraSessionDep,
) -> list[Compras]:
    table = cassandra_db.get_table("compras")
    result: Iterable[Compras] | object = await table.find(
        {"$and": [{"user_id": user_id}]}
    ).to_list()
    for resultado in result:
        print(resultado)
        resultado["data_compra"] = resultado["data_compra"].to_datetime(tz=datetime.UTC)
        print(Compras(**resultado))

    return list(result)
