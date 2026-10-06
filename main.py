from fastapi import FastAPI

from routes import router as authentication_router

app = FastAPI()

app.include_router(authentication_router)