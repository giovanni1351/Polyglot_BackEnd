from fastapi import FastAPI
from uvicorn import run

from core.database import create_db_and_tables
from routes import Token, User

app = FastAPI()
app.include_router(Token.router)
app.include_router(User.router)


@app.on_event("startup")
async def on_startup() -> None:
    await create_db_and_tables()


if __name__ == "__main__":
    run("main:app")
