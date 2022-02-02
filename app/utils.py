from fastapi import status, HTTPException
from passlib.context import CryptContext
import re

# tell passlib what hashing algorithm to use
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str):
    if re.fullmatch(r"[A-Za-z0-9!@#$%^&+=]{8,}", password):
        return password
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[
                "At least 8 characters",
                "Contain uppercase letters: A-Z",
                "Lowercase letters: a-z",
                "Numbers: 0-9",
                "Any of the special characters: !@#$%^&+=",
            ],
        )
