from fastapi import APIRouter, HTTPException, status, Depends

from app.oauth2 import get_current_user

from ..schema import UserOut, Vote
from .. import models
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id==vote.post_id).first()
    if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not Found"
            )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    vote_found = vote_query.first()
    if vote.dir == 1:
        if vote_found:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Vote already present"
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"Voted Successfully"}
    else:
        if not vote_found:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Vote does not exist"
            )
        db.delete(vote)
        db.commit()
        return {"message":"Successfully Deleted Vote"}