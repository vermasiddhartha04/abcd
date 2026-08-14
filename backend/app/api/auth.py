from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import (
    login_user,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/")
def auth_home():
    return {
        "module": "Authentication",
        "status": "working",
    }


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        new_user = register_user(
            db=db,
            user=user,
        )

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "email": new_user.email,
                "username": new_user.username,
                "role": new_user.role,
                "is_active": new_user.is_active,
            },
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    token = login_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return token


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.get("/profile")
def profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": "User Profile",
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
            "is_active": current_user.is_active,
        },
    }


@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Welcome Admin",
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
        },
    }