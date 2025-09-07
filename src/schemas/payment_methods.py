from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from schemas.user import User


class PagamentoCreate(SQLModel):
    user_id: int
    numero_cartao: str
    nome_titular: str
    data_validade: datetime
    cod_seguranca: int


class Pagamento(PagamentoCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="pagamentos")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=None)
