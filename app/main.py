from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.logging_config import logger
from app.schemas import UserCreate, UserResponse, URLInfo
from app.database import init_db
import os

app = FastAPI(title="FastAPI with PostgreSQL & K8s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for production)
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],   # Allow all headers
)

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

@app.get("/user", response_class=HTMLResponse)
async def root():
    logger.info("Root endpoint accessed")
    with open(os.path.join("app/templates", "index1.html"), "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/stats/{short_key}", response_model=URLInfo)
async def get_url_stats(short_key: str):
    print("Current stored URLs:", url_mapping)  # Debugging line

    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_data = url_mapping[short_key]
    return {
        "url": url_data["url"],
        "short_url": f"http://127.0.0.1:8000/{short_key}",
        "access_count": url_data["access_count"],
    }


app.include_router(router)
