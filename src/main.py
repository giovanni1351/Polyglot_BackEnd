from fastapi import FastAPI
from uvicorn import run

from core.database import create_db_and_tables
from routes import payment_methods, token, user
from schemas.payment_methods import PagamentoPublic  # noqa: F401
from schemas.user import UserWithRelations
from settings import Settings

UserWithRelations.model_rebuild()

app = FastAPI()
app.include_router(token.router)
app.include_router(user.router)
app.include_router(payment_methods.router)


@app.on_event("startup")
async def on_startup() -> None:
    await create_db_and_tables()


if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_certfile=Settings().CERT_PEM,
        ssl_keyfile=Settings().KEY_PEM,
    )
