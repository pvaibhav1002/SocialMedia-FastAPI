from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from ..schema import TokenSent
from .. import models
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from ..utils import verify_password
from ..oauth2 import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login",response_model=TokenSent)
def login(user_credentials: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    if not verify_password(user_credentials.password, user.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = create_access_token(data={"user_id": user.id})
    return access_token
