from datetime import timedelta

from fastapi import APIRouter, Depends , HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError ,IntegrityError
from sentry_sdk import capture_exception
from ..database import session_opener
from .schemas import UserAuthSchema
from ..auth.models import User

from ..auth.service import (
    validate_user_credentials,
    create_access_token,
    pwd_context,
    authenticate_user_token
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(session_opener)
):
    try:
        # 驗證用戶憑據
        user = validate_user_credentials(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        access_token = create_access_token(
            user_data={"sub": str(user.username)}, expires_delta=timedelta(minutes=1)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    except AttributeError as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred due to a missing attribute",
        )
    
    except HTTPException as e:
        capture_exception(e)
        raise

    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
    
@router.post("/register")
def create_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    try:
        # Hash the user's password
        hashed_password = pwd_context.hash(user.password)
        User.validate_username(user.username)
        User.validate_password(user.password)
        # Create a new user in the database
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError as e:  
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose another one.",
        )
    
    except SQLAlchemyError as e:  # Catch database-related errors
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user. Please try again later.",
        )
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
    
@router.get("/me")
def read_users_me(user=Depends(authenticate_user_token)):
    try:
        if not user or not hasattr(user, 'username'):
            raise AttributeError("User is not properly authenticated or username is missing.")

        return {"username": user.username}

    except AttributeError as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated or username is missing.",
        )
    except Exception as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )