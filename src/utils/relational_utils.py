from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from core.database import AsyncSession, AsyncSessionDep
from settings import LOGGER

# Decorator para logar o retorno da função e verificar se ocorreu algum erro


async def create_item[T](session: AsyncSession, model: type[T], data: dict) -> T | None:
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
    session: AsyncSession, model: type[T], item_id
) -> T | None:
    """Helper genérico para buscar"""
    item = await session.get(model, item_id)
    if not item:
        LOGGER.warning(f"{model.__name__} não encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    return item


async def update_item[T](
    session: AsyncSessionDep, model: type[T], data: dict
) -> T | None:
    item = await get_item_or_404(session, model, data["id"])
    for key, value in data.items():
        setattr(item, key, value)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_all_items[T](
    session: AsyncSession, model: type[T], **kwargs
) -> list[T] | None:
    """Helper genérico para buscar todos os itens"""
    try:
        query = select(model)
        for key, value in kwargs.items():
            query = query.where(getattr(model, key) == value)
        result = await session.exec(query)
        return result.all()
    except Exception as e:
        raise e


async def delete_item[T](session: AsyncSession, model: type[T], item_id) -> None:
    """Helper genérico para deletar"""
    item = await session.get(model, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} não encontrado",
        )
    await session.delete(item)
    await session.commit()


async def soft_delete_item[T](session: AsyncSession, model: type[T], item_id) -> None:
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


async def get_all_itens_by_in_clause[T](
    session: AsyncSession, model: type[T], column: str, ids: list[int]
) -> list[T] | None:
    """Helper genérico para buscar todos os ids"""
    query = select(model)
    query = query.where(getattr(model, column).in_(ids))
    result = await session.exec(query)
    return result.all()


async def remove_item_from_link_table[T](
    session: AsyncSession, model: type[T], item_ids: list[int]
) -> T | None:
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
