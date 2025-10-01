from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from core.auth import get_current_user
from schemas.products import Product, ProductCreate
from schemas.user import User

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/")
async def create_product(
    product: ProductCreate, current_user: Annotated[User, Depends(get_current_user)]
) -> Product:
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
    produtos = Product.find()
    return await produtos.to_list()


@router.get("/{product_id}")
async def get_product(
    product_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> Product:
    produto = await Product.find_one({"product_id": product_id})
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found by product id",
        )
    return produto
