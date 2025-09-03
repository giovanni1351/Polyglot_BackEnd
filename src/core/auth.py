import datetime
from datetime import timedelta
from time import timezone
from typing import Annotated, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import AsyncSessionDep
from schemas.Token import TokenData
from schemas.User import User
from settings import LOGGER, Settings
from utils.relational_utils import get_item_or_404

LOGGER.info("Criando o sistema de autenticação")
SECRET_KEY = Settings().SECRET_KEY
ALGORITHM = Settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Settings().ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
LOGGER.info("Sistema de autenticação criado com sucesso")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_item_or_404(session, User, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="User not admin")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str, session: AsyncSession):
    LOGGER.info(f"Autenticando usuário {username}")
    user = await get_item_or_404(session, User, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    LOGGER.info("Criando token de acesso")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )
    return encoded_jwt
