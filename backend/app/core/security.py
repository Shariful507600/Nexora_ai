# ============================================
# NEXORA AI - Security Module
# ============================================
# JWT token তৈরি ও যাচাই করা হয় এখানে।
# Password hashing ও verification এখানে।

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.logger import logger

# Password hashing context - bcrypt algorithm ব্যবহার করে
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",)

# OAuth2 token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """
    Plain password কে bcrypt hash এ রূপান্তর করে।
    Database এ কখনো plain password সংরক্ষণ করা হয় না।
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Login এর সময় user এর password যাচাই করে।
    plain password vs stored hash তুলনা করে।
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token তৈরি করে।
    data: token এ যা store করতে চাই (user_id, email)
    expires_delta: token কতক্ষণ valid থাকবে
    """
    to_encode = data.copy()

    # Token expiry time সেট করা
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # JWT token encode করা
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    JWT token decode করে user data বের করে।
    Token invalid বা expired হলে None return করে।
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    FastAPI dependency - প্রতিটি protected route এ ব্যবহার হয়।
    Token থেকে current user এর ID বের করে।
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    return int(user_id)
