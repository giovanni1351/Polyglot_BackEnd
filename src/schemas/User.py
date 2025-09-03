from datetime import datetime

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    name: str
    username: str
    email: str
    age: int
    cpf: str
    password: str
    endereco: str


class User(UserCreate, table=True):
    id: int | None = Field(primary_key=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=None)
