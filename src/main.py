from fastapi import FastAPI
from uvicorn import run

from core.database import create_db_and_tables
from routes import token, user

app = FastAPI()
app.include_router(token.router)
app.include_router(user.router)


@app.on_event("startup")
async def on_startup() -> None:
    await create_db_and_tables()


if __name__ == "__main__":
    run("main:app")
