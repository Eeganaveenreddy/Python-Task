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

router = APIRouter()

# In-memory storage for URL mappings
url_mapping = {}

class URLRequest(BaseModel):
    url: str
    expiry_minutes: int = None  # Optional expiry time

class URLInfo(BaseModel):
    url: str
    short_url: str
    access_count: int
    expiry_time: str = None
    

def generate_short_key(length=6):
    """Generate a random short key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/shorten/")
async def shorten_url(request: URLRequest):
    """Shorten a URL with optional expiry."""
    short_key = generate_short_key()
    expiry_time = None
    if request.expiry_minutes:
        expiry_time = datetime.utcnow() + timedelta(minutes=request.expiry_minutes)
    
    url_mapping[short_key] = {
        "url": str(request.url),
        "access_count": 0,
        "expiry_time": expiry_time
    }
    
    return {"short_url": f"http://127.0.0.1:8000/{short_key}"}

@router.get("/{short_key}")
async def redirect_to_original(short_key: str):
    """Redirect to the original URL and track usage."""
    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    url_data = url_mapping[short_key]

    # Check for expiry
    if url_data["expiry_time"] and datetime.utcnow() > url_data["expiry_time"]:
        del url_mapping[short_key]  # Remove expired URL
        raise HTTPException(status_code=410, detail="Short URL has expired")

    url_data["access_count"] += 1  # Increment access count
    return RedirectResponse(url=url_data["url"], status_code=302)

@router.get("/stats/{short_key}", response_model=URLInfo)
async def get_url_stats(short_key: str):
    """Get stats of a shortened URL."""
    if short_key not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    url_data = url_mapping[short_key]
    return {
        "url": url_data["url"],
        "short_url": f"http://127.0.0.1:8000/{short_key}",
        "access_count": url_data["access_count"],
        "expiry_time": url_data["expiry_time"].isoformat() if url_data["expiry_time"] else None
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
