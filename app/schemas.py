from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True

class URLInfo(BaseModel):
    url: str
    short_url: str
    access_count: int
