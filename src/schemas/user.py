from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.payment_methods import Pagamento, PagamentoPublic


class UserCreate(SQLModel):
    name: str
    username: str = Field(unique=True)
    email: str
    age: int
    cpf: str
    password: str
    endereco: str


class User(UserCreate, table=True):
    id: int = Field(primary_key=True)
    is_admin: bool = Field(default=False)
    pagamentos: list["Pagamento"] = Relationship(back_populates="user")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=None)


class UserPublic(UserCreate):
    id: int | None
    is_admin: bool
    created_at: datetime
    updated_at: datetime | None


class UserWithRelations(UserPublic):
    pagamentos: list["PagamentoPublic"] | None
