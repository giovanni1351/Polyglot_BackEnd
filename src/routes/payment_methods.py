from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select

from core.auth import get_current_admin
from core.database import AsyncSessionDep
from schemas.payment_methods import Pagamento, PagamentoCreate, PagamentoWithRelations
from schemas.user import User
from utils.relational_utils import create_item, get_item_or_404

router = APIRouter(prefix="/payment_method", tags=["payment_method"])


@router.post("/")
async def create_payment(
    metodo: PagamentoCreate,
    current_user: Annotated[User, Depends(get_current_admin)],
    session: AsyncSessionDep,
) -> Pagamento:
    await get_item_or_404(session, User, metodo.user_id)
    metodo.data_validade = metodo.data_validade.replace(tzinfo=None)
    pagamento = Pagamento(**metodo.model_dump())
    return await create_item(session, Pagamento, pagamento.model_dump())


@router.get("/")
async def get_payments(
    current_user: Annotated[User, Depends(get_current_admin)],
    session: AsyncSessionDep,
) -> list[PagamentoWithRelations]:
    return (
        await session.exec(select(Pagamento).options(selectinload(Pagamento.user)))
    ).all()
