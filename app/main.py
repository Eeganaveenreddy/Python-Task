from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.logging_config import logger
from app.database import init_db
import random
import string
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os

app = FastAPI(title="FastAPI with PostgreSQL & K8s")

router = APIRouter()
 
# In-memory storage for URL mappings
url_mapping = {}
 
class URLRequest(BaseModel):
    url: str
 
def generate_short_key(length=6):
    """Generate a random short key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
 
@router.post("/shorten/")
async def shorten_url(request: URLRequest):
    """Shorten a URL and store the mapping dynamically"""
    short_key = generate_short_key()  # Generate a unique short key
    url_mapping[short_key] = request.url  # Store the mapping
    return {"short_url": f"http://127.0.0.1:8080/{short_key}"}
 
@router.get("/{short_key}")
async def redirect_to_original(short_key: str):
    """Redirect to the original URL"""
    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
   
    original_url = url_mapping[short_key]
    return RedirectResponse(url=original_url, status_code=302)

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
