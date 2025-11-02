from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from core.auth import get_current_user
from core.database import ensure_beanie_initialized
from schemas.products import Product, ProductCreate, ProductUpdate
from schemas.responses import DeleteResponse
from schemas.user import User

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/")
async def create_product(
    product: ProductCreate, current_user: Annotated[User, Depends(get_current_user)]
) -> Product:
    await ensure_beanie_initialized()
    produto = Product(
        **product.model_dump(),
        owner_id=current_user.id if current_user.id is not None else -1,
    )
    try:
        await produto.insert()
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Produto ja existente"
        ) from e

    return produto


@router.get("/")
async def get_products(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Product]:
    await ensure_beanie_initialized()
    produtos = Product.find()
    return await produtos.to_list()


@router.get("/{product_id}")
async def get_product(
    product_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> Product:
    await ensure_beanie_initialized()
    produto = await Product.find_one({"product_id": product_id})
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found by product id",
        )
    return produto


@router.delete("/{product_id}")
async def delete_product(
    product_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> DeleteResponse:
    await ensure_beanie_initialized()
    produto = await Product.find_one({"product_id": product_id})
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found by product id",
        )
    result = await produto.delete()
    print(result)
    return DeleteResponse(message=f"Produto {product_id = } deletado com sucesso")


@router.put("/{product_id}")
async def put_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Product:
    await ensure_beanie_initialized()
    produto = await Product.find_one({"product_id": product_id})
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found by product id",
        )
    if product_data.nome is not None:
        produto.nome = product_data.nome
    if product_data.preco is not None:
        produto.preco = product_data.preco
    if product_data.marca is not None:
        produto.marca = product_data.marca
    if product_data.desc is not None:
        produto.desc = product_data.desc
    produto.updated_at = datetime.now()
    result = await produto.save()
    print(result)
    return produto
