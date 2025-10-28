from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import AsyncSessionDep
from schemas.token import TokenData
from schemas.user import User
from settings import SETTINGS

SECRET_KEY = SETTINGS.SECRET_KEY
ALGORITHM = SETTINGS.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(  # type: ignore
            token,
            SETTINGS.SECRET_KEY,  # type: ignore
            algorithms=[SETTINGS.ALGORITHM],  # type: ignore
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = (
        await session.exec(select(User).where(User.email == token_data.email))
    ).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not admin"
        )
    return current_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> User | Literal[False]:
    user = (await session.exec(select(User).where(User.username == username))).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # type: ignore
    return jwt.encode(to_encode, SETTINGS.SECRET_KEY, algorithm=SETTINGS.ALGORITHM)  # type: ignore
