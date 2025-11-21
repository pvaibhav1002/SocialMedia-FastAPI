from fastapi import  APIRouter, HTTPException,  status

from ..utils import hash_password
from ..schema import User, UserOut
from .. import models
from ..database import engine, get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: User, db: Session = Depends(get_db)):
    user.password = hash_password(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}",response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} not found",
        )
    return user
