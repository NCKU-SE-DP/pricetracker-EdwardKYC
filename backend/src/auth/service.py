from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError , ExpiredSignatureError
import logging

from sqlalchemy.orm import Session

from ..database import session_opener
from .config import auth_config
from .models import User
from passlib.context import CryptContext
from sentry_sdk import capture_exception

# 配置 logger，將日誌輸出到 console 和檔案
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
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查詢用戶
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"User not found for token: {username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        logger.info(f"User {username} authenticated successfully with token")
        return user
    
    except ExpiredSignatureError as e:
        capture_exception(e)
        logger.error(f"Token has expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    except JWTError as e:
        capture_exception(e)
        logger.error(f"Invalid token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error during token authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

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
    
    except AttributeError as e:
        capture_exception(e)
        logger.error(f"Attribute error while creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating the access token",
        )
    
    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error while creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )