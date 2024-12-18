from datetime import timedelta

from fastapi import APIRouter, Depends , HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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
    """
    Registers a new user with a hashed password.

    :param user: User data containing username and password.
    :param db: Database session dependency.
    :return: The created user object.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me")
def read_users_me(user=Depends(authenticate_user_token)):
    return {"username": user.username}