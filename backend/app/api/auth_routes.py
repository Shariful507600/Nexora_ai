# ============================================
# NEXORA AI - Authentication Routes
# ============================================
# User registration, login, logout endpoints।

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

from app.database.postgres_db import get_db
from app.models.user import User
from app.core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user_id
)
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================
# Request/Response Schemas
# ============================================
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    email: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime


# ============================================
# Registration Endpoint
# ============================================
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    নতুন user register করে।
    Email duplicate check করে।
    Password hashed করে store করে।
    """
    # Email already exists কিনা check
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="এই email দিয়ে আগেই account আছে।"
        )

    # Password validation
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password অন্তত ৬ character হতে হবে।"
        )

    # New user তৈরি করা
    new_user = User(
        full_name=request.full_name,
        email=request.email,
        hashed_password=hash_password(request.password),
    )

    db.add(new_user)
    await db.flush()    # ID generate করতে
    await db.refresh(new_user)

    logger.info(f"✅ New user registered: {new_user.email}")

    return new_user


# ============================================
# Login Endpoint
# ============================================
@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    User login করে JWT token দেয়।
    OAuth2 password flow ব্যবহার করে।
    """
    # User খোঁজা
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # Email বা password ভুল
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email বা password ভুল।",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Account active কিনা check
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deactivated।"
        )

    # Last login update
    user.last_login = datetime.utcnow()

    # JWT token তৈরি
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"✅ User logged in: {user.email}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )


# ============================================
# Get Current User
# ============================================
@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Current logged-in user এর তথ্য।"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
