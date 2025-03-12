from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.logging_config import logger
from app.database import init_db
import os

app = FastAPI(title="FastAPI with PostgreSQL & K8s")

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Application startup completed")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("Root endpoint accessed")
    with open(os.path.join("app/templates", "index.html"), "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

app.include_router(router)
