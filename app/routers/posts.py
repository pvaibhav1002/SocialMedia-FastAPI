from typing import Optional
from fastapi import HTTPException, Response, status, APIRouter
from sqlalchemy import func

from app import oauth2
from app.oauth2 import get_current_user
from ..schema import Post, PostResponse, PostVote, UserOut
from .. import models
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/posts", tags=["Posts"])


# @router.get("/", response_model=list[PostResponse])
@router.get("", response_model=list[PostVote])
def get_posts(
    db: Session = Depends(get_db),
    user: UserOut = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = "",
):
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(offset).all()
    query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
    )
    results = db.execute(query).mappings().all()
    return results


@router.get("/{id}", response_model=PostVote)
def get_single_post(
    id: int, db: Session = Depends(get_db), user: UserOut = Depends(get_current_user)
):
    query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
    )
    post = db.execute(query).mappings().first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
    return post


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=PostResponse
)
def create_post(
    post: Post, db: Session = Depends(get_db), user: UserOut = Depends(get_current_user)
):
    post_dict = post.model_dump()
    new_post = models.Post(user_id=user.id, **post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    user: UserOut = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
    if post.user_id != user.id:  # type:ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Action"
        )
    db.delete(post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=Post)
def update_post(
    id: int,
    updated_post: Post,
    db: Session = Depends(get_db),
    user: UserOut = Depends(get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
    if post.user_id != user.id:  # type:ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Action"
        )
    post_query.update(updated_post.model_dump(), synchronize_session=False)  # type: ignore
    db.commit()
    return post_query.first()
