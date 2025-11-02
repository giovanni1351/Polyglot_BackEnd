from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from uvicorn import run

from core.database import create_db_and_tables, init_astra_cassandra
from routes import compras, payment_methods, products, token, user
from schemas.payment_methods import PagamentoPublic  # type: ignore # noqa: F401
from schemas.user import UserWithRelations
from settings import SETTINGS

UserWithRelations.model_rebuild()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await init_astra_cassandra()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(token.router)
app.include_router(user.router)
app.include_router(payment_methods.router)
app.include_router(products.router)
app.include_router(compras.router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema: dict[str, Any] = get_openapi(
        title="Polyglot BACKEND",
        version="1.0.0",
        summary="Sistema de e-comercie",
        description="""Trabalho de estudo para a criacao de uma api onde se
         comunica com varios bancos de dados, entre eles, postgres, mongo db
          e cassandra""",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        port=8000,
        ssl_certfile=SETTINGS.CERT_PEM,
        ssl_keyfile=SETTINGS.KEY_PEM,
    )
