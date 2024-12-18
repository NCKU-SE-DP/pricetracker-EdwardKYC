import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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

# 設定 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 設定日誌格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 創建 FileHandler，將日誌寫入 app.log
file_handler = logging.FileHandler('app.log', mode='a')  # 'a' 表示追加日誌到文件中
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 創建 StreamHandler，將日誌輸出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

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

    except AttributeError as e:
        capture_exception(e)
        logger.error(f"AttributeError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred due to a missing attribute",
        )

    except HTTPException as e:
        capture_exception(e)
        logger.error(f"HTTPException: {str(e.detail)}")
        raise

    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

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

    except IntegrityError as e:
        capture_exception(e)
        logger.error(f"IntegrityError: Username {user.username} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose another one.",
        )

    except SQLAlchemyError as e:  # Catch database-related errors
        capture_exception(e)
        logger.error(f"SQLAlchemyError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user. Please try again later.",
        )

    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )

@router.get("/me")
def read_users_me(user=Depends(authenticate_user_token)):
    try:
        logger.info(f"Fetching information for user: {user.username}")

        if not user or not hasattr(user, 'username'):
            raise AttributeError("User is not properly authenticated or username is missing.")
        
        logger.info(f"User {user.username} successfully fetched.")
        return {"username": user.username}

    except AttributeError as e:
        capture_exception(e)
        logger.error(f"AttributeError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated or username is missing.",
        )

    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )