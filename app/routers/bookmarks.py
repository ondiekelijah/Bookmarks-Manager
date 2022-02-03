from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import validators
from .. import models, schemas, oath2
from ..database import get_db

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

# Get bookmark stats
@router.get("/stats")
def bookmark_stats(
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user),
):
    data = []

    items = (
        db.query(models.Bookmarks)
        .filter(models.Bookmarks.user_id == current_user.id)
        .all()
    )

    for item in items:
        new_link = {
            "visits": item.visits,
            "url": item.url,
            "id": item.id,
            "short_url": item.short_url,
        }

        data.append(new_link)

    return data


# Fetch all user bookmarks


@router.get("/", response_model=List[schemas.Bookmark])
def get_user_bookmarks(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    current_user: int = Depends(oath2.get_current_user),
):

    bookmarks = (
        db.query(models.Bookmarks)
        .group_by(models.Bookmarks.id)
        .filter(
            models.Bookmarks.user_id == current_user.id,
            or_(
                models.Bookmarks.body.ilike(f"%{search}%"),
                models.Bookmarks.url.ilike(f"%{search}%"),
                models.Bookmarks.short_url.ilike(f"%{search}%"),
            ),
        )
        .limit(limit)
        .offset(skip)
        .all()
    )

    return bookmarks


#  Create a new Bookmark


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.BookmarkOut)
def create_bookmark(
    bookmark: schemas.BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user),
):

    if not validators.url(bookmark.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please provide a valid URL",
        )

    if db.query(models.Bookmarks).filter(models.Bookmarks.url == bookmark.url).first():

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bookmark already exists",
        )

    try:
        new_bookmark = models.Bookmarks(user_id=current_user.id, **bookmark.dict())
        db.add(new_bookmark)
        db.commit()
        db.refresh(new_bookmark)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}",
        )

    return new_bookmark


# Fetch Bookmark by id


@router.get("/{id}", response_model=schemas.Bookmark)
def get_bookmark(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user),
):

    bookmark = db.query(models.Bookmarks).filter(models.Bookmarks.id == id).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark with id:{id} is not available",
        )

    return bookmark


# Update Bookmark


@router.put("/{id}", response_model=schemas.BookmarkOut)
def update_bookmark(
    id: int,
    updated_post: schemas.BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user),
):

    bookmark_query = db.query(models.Bookmarks).filter(models.Bookmarks.id == id)

    bookmark = bookmark_query.first()

    if bookmark == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark with id:{id} was not found",
        )

    if bookmark.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    bookmark_query.update(
        updated_post.dict(),
        synchronize_session=False,
    )

    db.commit()

    return bookmark_query.first()


# Delete Bookmark


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user),
):

    bookmark_query = db.query(models.Bookmarks).filter(models.Bookmarks.id == id)

    bookmark = bookmark_query.first()

    if bookmark == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark with id:{id} was not found",
        )

    if bookmark.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    bookmark_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
