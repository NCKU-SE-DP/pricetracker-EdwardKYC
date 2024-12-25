from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError , ExpiredSignatureError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sentry_sdk import capture_exception

from ..database import session_opener
from .config import auth_config
from .models import User
from ..logger.base import logger
from ..error import handle_http_exception , handle_token_exception , handle_access_token_exception
import logging

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
        logger.debug(f"Decoding token: {token[:10]}...")  # 只顯示token的前幾個字符
        payload = jwt.decode(token, auth_config.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token missing 'sub' field")
            handle_http_exception   (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查詢用戶
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"User not found for token: {username}")
            handle_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        logger.info(f"User {username} authenticated successfully with token")
        return user
    
    except Exception as e:
        handle_token_exception(e)

def create_access_token(user_data, expires_delta=None):
    try:
        to_encode = user_data.copy()
        
        # 設定過期時間
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        # 編碼 JWT
        encoded_jwt = jwt.encode(to_encode, "your_secret_key", algorithm="HS256")
        logger.info(f"Access token created for user: {user_data['sub']}")
        return encoded_jwt
    
    except Exception as e:
        handle_access_token_exception(e)