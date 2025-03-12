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
