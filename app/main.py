from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine, get_db
from .models import Bookmarks
from .routers import user, auth, bookmarks


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookmarks.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message" : "Hello, mate, follow me on Twitter @dev_elie"}


@app.get("/find/{short_url}")
def redirect(short_url: str, db: Session = Depends(get_db)):

    bookmark = db.query(Bookmarks).filter(Bookmarks.short_url == short_url).first()

    if bookmark:
        bookmark.visits =  bookmark.visits + 1
        db.commit()

    response = RedirectResponse(url=bookmark.url)

    return response



