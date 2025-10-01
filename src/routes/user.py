from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from core.auth import get_current_user, get_password_hash
from core.database import AsyncSessionDep
from schemas.payment_methods import Pagamento, PagamentoCreate
from schemas.user import User, UserCreate, UserWithRelations
from utils.relational_utils import create_item

router = APIRouter(prefix="/user", tags=["user"])


class UserRegisterError(Exception): ...


@router.post("/")
async def create_user(user: UserCreate, session: AsyncSessionDep) -> User:
    user.password = get_password_hash(user.password)
    return await create_item(session, User, user.model_dump())


@router.get("/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)], session: AsyncSessionDep
) -> UserWithRelations:
    user: User | None = (
        await session.exec(
            select(User)
            .options(selectinload(User.pagamentos))  # type: ignore
            .where(User.id == current_user.id)
        )
    ).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User não encontrado",
        )
    return user  # type: ignore


@router.post("/payment_method")
async def create_payment(
    metodo: PagamentoCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSessionDep,
) -> Pagamento:
    metodo.user_id = current_user.id if current_user.id is not None else -1
    metodo.data_validade = metodo.data_validade.replace(tzinfo=None)
    pagamento = Pagamento(**metodo.model_dump())
    return await create_item(session, Pagamento, pagamento.model_dump())
