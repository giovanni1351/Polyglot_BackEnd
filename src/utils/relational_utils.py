from collections.abc import Sequence
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import SQLModel, select

from core.database import AsyncSession

# Decorator para logar o retorno da função e verificar se ocorreu algum erro


async def create_item[T](
    session: AsyncSession, model: type[T], data: dict[str, Any]
) -> T:
    """Helper genérico para criar"""
    if hasattr(model, "created_at"):
        data["created_at"] = datetime.now()
    if hasattr(model, "updated_at"):
        data["updated_at"] = datetime.now()

    item: T = model(**data)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_item_or_404[T](
    session: AsyncSession, model: type[T], item_id: int | float | str
) -> T | None:
    """Helper genérico para buscar"""
    item = await session.get(model, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    return item


async def update_item[T](
    session: AsyncSession, model: type[T], data: dict[str, Any]
) -> T | None:
    item = await get_item_or_404(session, model, data["id"])
    for key, value in data.items():
        setattr(item, key, value)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_all_items[T](
    session: AsyncSession, model: type[T], **kwargs: dict[Any, Any]
) -> Sequence[T] | None:
    """Helper genérico para buscar todos os itens"""
    query = select(model)
    for key, value in kwargs.items():
        query = query.where(getattr(model, key) == value)
    result = await session.exec(query)
    return result.all()


async def delete_item[T](
    session: AsyncSession, model: type[T], item_id: int | str | float
) -> None:
    """Helper genérico para deletar"""
    item = await session.get(model, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    await session.delete(item)
    await session.commit()


async def soft_delete_item[T: SQLModel](
    session: AsyncSession, model: type[T], item_id: int | str
) -> None:
    """Helper genérico para deletar"""
    item = await session.get(model, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    item.deleted_at = datetime.now()
    session.add(item)
    await session.commit()


async def get_all_itens_by_in_clause[T: SQLModel](
    session: AsyncSession, model: type[T], column: str, ids: list[int]
) -> Sequence[T]:
    """Helper genérico para buscar todos os ids"""
    query = select(model)
    query = query.where(getattr(model, column).in_(ids))
    result = await session.exec(query)
    return result.all()


async def remove_item_from_link_table[T: SQLModel](
    session: AsyncSession, model: type[T], item_ids: list[int]
) -> T:
    """Helper genérico para deletar"""
    item = await session.get(model, item_ids)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    await session.delete(item)
    await session.commit()
    return item
