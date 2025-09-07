from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.payment_methods import Pagamento


class UserCreate(SQLModel):
    name: str
    username: str = Field(unique=True)
    email: str
    age: int
    cpf: str
    password: str
    endereco: str


class User(UserCreate, table=True):
    id: int | None = Field(primary_key=True)
    is_admin: bool = Field(default=False)
    pagamentos: list["Pagamento"] = Relationship(back_populates="user")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=None)
