from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes import profile, auth
import uvicorn
from db.db import db
from db import migrations
from routes import convo
from routes import household

@asynccontextmanager
async def lifespan(app: FastAPI):
    migrations.migrate()
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.include_router(profile.router)
app.include_router(auth.router)
app.include_router(convo.router)
app.include_router(household.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)