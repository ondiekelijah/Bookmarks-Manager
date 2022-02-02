from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# Handles the user sending data to us
class BookmarkBase(BaseModel):
    body: str
    url: str



class BookmarkCreate(BookmarkBase):
    pass


# Handles us sending back data to the users


class Bookmark(BookmarkBase):
    id: int
    short_url: str
    visits: str
    created_at: datetime
    user: UserOut

    class Config:
        orm_mode = True


