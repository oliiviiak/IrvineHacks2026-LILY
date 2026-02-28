from fastapi import FastAPI
from routes import profile
import uvicorn

app = FastAPI()

app.include_router(profile.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)