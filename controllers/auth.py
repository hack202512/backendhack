from datetime import timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from models.models import User
from functions.auth import get_password_hash, verify_password, create_access_token, get_current_user_token
from schemas.auth_schemas import RegisterRequest, LoginRequest, UserResponse
from context.db import get_db


router = APIRouter(prefix="/auth", tags=["auth"])

def get_user_role(user: User) -> str:
    if hasattr(user, 'role') and user.role:
        return user.role.value if hasattr(user.role, "value") else str(user.role)
    return "user"

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(payload.password)

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=get_user_role(user),
    )


@router.post("/login")
def login_user(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_expires = timedelta(hours=2)
    refresh_expires = timedelta(hours=10)

    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": get_user_role(user),
    }

    access_token = create_access_token(token_data, expires_delta=access_expires)
    refresh_token = create_access_token(
        {**token_data, "type": "refresh"},
        expires_delta=refresh_expires,
    )

    db_url = os.getenv("DATABASE_URL", "")
    is_production = db_url and "localhost" not in db_url and "127.0.0.1" not in db_url
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(access_expires.total_seconds()),
        samesite="none" if is_production else "lax",
        secure=is_production,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=int(refresh_expires.total_seconds()),
        samesite="none" if is_production else "lax",
        secure=is_production,
        path="/",
    )

    return {"detail": "Logged in successfully"}


@router.get("/me")
def get_current_user(
    request: Request,
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == token_data.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=get_user_role(user),
    )


@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    
    try:
        from functions.auth import decode_access_token
        payload = decode_access_token(refresh_token_value)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        access_expires = timedelta(hours=2)
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "role": get_user_role(user),
        }
        
        access_token = create_access_token(token_data, expires_delta=access_expires)
        
        db_url = os.getenv("DATABASE_URL", "")
        is_production = db_url and "localhost" not in db_url and "127.0.0.1" not in db_url
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=int(access_expires.total_seconds()),
            samesite="none" if is_production else "lax",
            secure=is_production,
            path="/",
        )
        
        return {"detail": "Token refreshed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
def logout_user(response: Response):
    db_url = os.getenv("DATABASE_URL", "")
    is_production = db_url and "localhost" not in db_url and "127.0.0.1" not in db_url
    
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="none" if is_production else "lax",
        secure=is_production,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="none" if is_production else "lax",
        secure=is_production,
    )
    return {"detail": "Logged out successfully"}

