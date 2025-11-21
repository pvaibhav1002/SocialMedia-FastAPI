from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint


# User
class User(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


# Post
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


class PostResponse(Post):
    id: int
    created_at: datetime
    user_id: int
    user: UserOut

    model_config = {"from_attributes": True}


class PostVote(BaseModel):
    Post: PostResponse
    votes: int

    model_config = {"from_attributes": True}


# Authentication
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# OAuth
class TokenSent(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenReceived(BaseModel):
    id: Optional[int] = None


# Vote
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  # type:ignore
