import logging
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sentry_sdk import capture_exception
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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
from ..logger.base import logger
from ..error import handle_request_exception
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
        logger.info(f"Login attempt for user: {form_data.username}")

        # 驗證用戶憑據
        user = validate_user_credentials(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Invalid login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        
        access_token = create_access_token(
            user_data={"sub": str(user.username)}, expires_delta=timedelta(minutes=1)
        )
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        # 驗證用戶憑據
        user = validate_user_credentials(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Invalid login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        
        access_token = create_access_token(
            user_data={"sub": str(user.username)}, expires_delta=timedelta(minutes=1)
        )
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        handle_request_exception(e, "login for access token")


@router.post("/register")
def create_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    try:
        logger.info(f"Attempting to create user: {user.username}")

        # Hash the user's password
        hashed_password = pwd_context.hash(user.password)
        User.validate_username(user.username)
        User.validate_password(user.password)

        # Create a new user in the database
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User {user.username} created successfully.")
        return db_user
        # Hash the user's password
        hashed_password = pwd_context.hash(user.password)
        User.validate_username(user.username)
        User.validate_password(user.password)

        # Create a new user in the database
        db_user = User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User {user.username} created successfully.")
        return db_user

    except Exception as e:
        handle_request_exception(e, "create user")

@router.get("/me")
def read_users_me(user=Depends(authenticate_user_token)):
    try:
        logger.info(f"Fetching information for user: {user.username}")

        if not user or not hasattr(user, 'username'):
            raise AttributeError("User is not properly authenticated or username is missing.")
        
        logger.info(f"User {user.username} successfully fetched.")
        return {"username": user.username}

    except Exception as e:
        handle_request_exception(e, "fetch user details")