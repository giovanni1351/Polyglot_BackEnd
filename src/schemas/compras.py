from datetime import datetime

from astrapy import AsyncDatabase
from astrapy.info import ColumnType, CreateTableDefinition
from pydantic import BaseModel


async def criar_compras(cassadra_db: AsyncDatabase) -> None:
    try:
        cassadra_db.get_table("compras")
        print("Tabela 'compras' já existe, pulando criação")
        return
    except Exception:
        print("Tabela 'compras' não existe, criando...")

    await cassadra_db.create_table(
        name="compras",
        definition=CreateTableDefinition.builder()
        .add_column("user_id", ColumnType.INT)
        .add_column("quantidade", ColumnType.INT)
        .add_column("product_id", ColumnType.TEXT)
        .add_column("data_compra", ColumnType.TIMESTAMP)
        .add_column("valor_pago", ColumnType.DECIMAL)
        .add_column("valor_produto", ColumnType.DECIMAL)
        .add_partition_by(["user_id", "data_compra", "product_id"])
        .build(),
    )
    print("tabela criada")


class Compras(BaseModel):
    user_id: int
    product_id: str
    quantidade: int
    data_compra: datetime
    valor_pago: float
    valor_produto: float
