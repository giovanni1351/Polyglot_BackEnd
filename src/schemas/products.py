from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed  # type: ignore
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    nome: str
    preco: float
    marca: str
    desc: str | None
    product_id: str
    created_at: datetime = Field(default=datetime.now())


class Product(Document):
    owner_id: int
    nome: str
    preco: float
    marca: str
    desc: str | None
    created_at: datetime = Field(default=datetime.now())
    product_id: Annotated[str, Indexed(unique=True)]
    updated_at: datetime | None = None
