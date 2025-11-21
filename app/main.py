from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import votes
from . import models
from .database import engine
from app.routers import posts, users, auth,votes
from .config import settings

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello World"}
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(votes.router)