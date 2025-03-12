from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import UserCreate, UserResponse
from .logging_config import logger
import random
import string
import time

app = FastAPI()
router = APIRouter()

# In-memory storage for URL mappings and usage stats
url_mapping = {}
url_stats = {}

class URLRequest(BaseModel):
    url: str
    expiry_minutes: int | None = None  # Optional expiry

def generate_short_key(length=6):
    """Generate a random short key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/shorten/")
async def shorten_url(request: URLRequest):
    """Shorten a URL and store the mapping with optional expiry"""
    short_key = generate_short_key()
    expiry_time = None

    if request.expiry_minutes:
        expiry_time = time.time() + (request.expiry_minutes * 60)  # Store expiry in UNIX timestamp

    url_mapping[short_key] = {
        "url": request.url,
        "expiry_time": expiry_time
    }
    url_stats[short_key] = {"access_count": 0}

    return {"short_url": f"http://127.0.0.1:8000/{short_key}"}

@router.get("/{short_key}")
async def redirect_to_original(short_key: str):
    """Redirect to the original URL and track usage"""
    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_data = url_mapping[short_key]
    
    # Check if the URL is expired
    if url_data["expiry_time"] and time.time() > url_data["expiry_time"]:
        del url_mapping[short_key]  # Remove expired URL
        del url_stats[short_key]
        raise HTTPException(status_code=410, detail="Short URL expired")

    # Track the number of times accessed
    url_stats[short_key]["access_count"] += 1

    return RedirectResponse(url=url_data["url"], status_code=302)

@router.get("/stats/{short_key}")
async def get_url_stats(short_key: str):
    """Retrieve URL stats"""
    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_data = url_mapping[short_key]
    stats = url_stats[short_key]

    return {
        "url": url_data["url"],
        "access_count": stats["access_count"],
        "expiry_time": url_data["expiry_time"]
    }
    
@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating user: {user.name}")
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"User {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
