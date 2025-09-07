from typing import Annotated

from fastapi import APIRouter, Depends

from core.auth import get_current_user, get_password_hash
from core.database import AsyncSessionDep
from schemas.user import User, UserCreate
from utils.relational_utils import create_item

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/")
async def create_user(user: UserCreate, session: AsyncSessionDep) -> User:
    user.password = get_password_hash(user.password)
    return await create_item(session, User, user.model_dump())


@router.get("/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
