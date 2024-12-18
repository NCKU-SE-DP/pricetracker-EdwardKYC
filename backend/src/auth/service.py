from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError , ExpiredSignatureError

from sqlalchemy.orm import Session

from ..database import session_opener
from .config import auth_config
from .models import User
from passlib.context import CryptContext
from sentry_sdk import capture_exception

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=auth_config.AUTH_TOKEN_URL)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def validate_user_credentials(db_session: Session, username: str, password: str):
    user = db_session.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def authenticate_user_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(session_opener),
):
    try:
        # 嘗試解碼 JWT
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查詢用戶
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )    
        return user
    
    except ExpiredSignatureError as e:
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    except JWTError as e:
        # 處理 JWT 解碼失敗的情況並記錄到 Sentry
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # 捕獲其他可能的例外並記錄到 Sentry
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )



def create_access_token(user_data, expires_delta=None):
    to_encode = user_data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)
    return encoded_jwt