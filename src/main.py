from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from core.database import create_db_and_tables
from routes import payment_methods, products, token, user
from schemas.payment_methods import PagamentoPublic  # type: ignore # noqa: F401
from schemas.user import UserWithRelations
from settings import SETTINGS

UserWithRelations.model_rebuild()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(token.router)
app.include_router(user.router)
app.include_router(payment_methods.router)
app.include_router(products.router)


if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_certfile=SETTINGS.CERT_PEM,
        ssl_keyfile=SETTINGS.KEY_PEM,
    )
