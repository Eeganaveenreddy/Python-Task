from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.logging_config import logger

router = APIRouter()

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