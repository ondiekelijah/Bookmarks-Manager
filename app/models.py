from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
import string
import random

from .database import Base , get_db


class Bookmarks(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    body = Column(String, nullable=False)
    url = Column(String, nullable=False)
    short_url = Column(String, nullable=False)
    visits = Column(Integer, nullable=False, default=0)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User")

    def generate_short_characters(self):
        """Find a way of getting all the possible characters, and picking a unique 3"""

        characters = string.digits + string.ascii_letters
        picked_chars = "".join(random.choices(characters, k=3))

        link = next(get_db()).query(Bookmarks).filter(self.short_url == picked_chars).first()

        if link:
            self.generate_short_characters()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url = self.generate_short_characters()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
