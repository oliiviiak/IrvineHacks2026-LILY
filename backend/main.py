from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes import profile, auth
import uvicorn
from db.db import db
from db import migrations
from routes import convo
from routes import households
from routes import transcript
from routes import document

@asynccontextmanager
async def lifespan(app: FastAPI):
    migrations.migrate()
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.include_router(profile.router)
app.include_router(auth.router)
app.include_router(convo.router)
app.include_router(households.router)
app.include_router(transcript.router)
app.include_router(document.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)