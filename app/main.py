from fastapi import FastAPI
from app.routes import router
from app.logging_config import logger
from app.database import init_db
import os

app = FastAPI(title="FastAPI with PostgreSQL & K8s")

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Application startup completed")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, FastAPI!"}

app.include_router(router)