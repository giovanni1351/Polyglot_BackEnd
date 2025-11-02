import datetime
from collections.abc import Iterable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from core.auth import get_current_user, get_password_hash
from core.database import AsyncSessionDep, CassandraSessionDep
from schemas.compras import Compras
from schemas.payment_methods import Pagamento, PagamentoCreateLogin
from schemas.responses import DeleteResponse
from schemas.user import User, UserCreate, UserWithRelations
from utils.relational_utils import create_item

router = APIRouter(prefix="/user", tags=["user"])


class UserRegisterError(Exception): ...


@router.post("/")
async def create_user(user: UserCreate, session: AsyncSessionDep) -> User:
    user.password = get_password_hash(user.password)
    user_exist: User | None = (
        await session.exec(select(User).where(User.username == user.username))
    ).first()
    if user_exist is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already registred"
        )
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
    metodo: PagamentoCreateLogin,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSessionDep,
) -> Pagamento:
    metodo_verificando = await session.exec(
        select(Pagamento).where(Pagamento.numero_cartao == metodo.numero_cartao)
    )
    if len(metodo_verificando.all()) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Method already registred, try with another card number",
        )

    metodo.data_validade = metodo.data_validade.replace(tzinfo=None)
    pagamento = Pagamento(**metodo.model_dump(), user_id=current_user.id)
    return await create_item(session, Pagamento, pagamento.model_dump())


@router.get("/payment_method/{payment_id}")
async def get_payment(
    payment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSessionDep,
) -> Pagamento:
    pagamento = (
        await session.exec(
            select(Pagamento)
            .where(Pagamento.id == payment_id)
            .where(Pagamento.user_id == current_user.id)
        )
    ).first()
    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metodo de pagamento não encontrado pelo ID",
        )

    return pagamento


@router.get("/payment_method")
async def get_payments(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSessionDep,
) -> list[Pagamento]:
    pagamentos = (
        await session.exec(
            select(Pagamento).where(Pagamento.user_id == current_user.id)
        )
    ).fetchall()
    if not pagamentos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metodo de pagamento não encontrado pelo ID",
        )

    return list[Pagamento](pagamentos)


@router.delete("/payment_method/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSessionDep,
) -> DeleteResponse:
    pagamento = (
        await session.exec(
            select(Pagamento)
            .where(Pagamento.id == payment_id)
            .where(Pagamento.user_id == current_user.id)
        )
    ).first()
    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metodo de pagamento não encontrado pelo ID",
        )
    await session.delete(pagamento)
    await session.commit()

    return DeleteResponse(message="Payment method deleted sucesfully")


@router.get("/compras")
async def get_compras_user(
    current_user: Annotated[User, Depends(get_current_user)],
    cassandra_db: CassandraSessionDep,
) -> list[Compras]:
    table = cassandra_db.get_table("compras")
    result: Iterable[Compras] | object = await table.find(
        {"$and": [{"user_id": current_user.id}]}
    ).to_list()
    for resultado in result:
        print(resultado)
        resultado["data_compra"] = resultado["data_compra"].to_datetime(tz=datetime.UTC)
        print(Compras(**resultado))

    return list(result)
