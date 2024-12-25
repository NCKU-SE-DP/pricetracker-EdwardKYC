from fastapi import HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from sentry_sdk import capture_exception
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from logger.base import logger

def raise_validation_error(field_name: str, max_length: int):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{field_name.capitalize()} exceeds the maximum length of {max_length} characters."
    )

def handle_http_exception(status_code, detail, headers=None):
    """
    通用的 HTTPException 處理函數。
    :param status_code: HTTP 狀態碼
    :param detail: 錯誤細節
    :param headers: 可選的 HTTP headers
    :raise HTTPException: 使用統一的格式拋出異常
    """
    logger.error(f"HTTP Exception: {status_code} - {detail}")
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers,
    )

def handle_token_exception(exception: Exception):
    """
    通用的 Token 錯誤處理函數。
    :param exception: 捕獲的異常
    """
    if isinstance(exception, ExpiredSignatureError):
        capture_exception(exception)
        handle_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    elif isinstance(exception, JWTError):
        capture_exception(exception)
        handle_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        capture_exception(exception)
        handle_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

def handle_access_token_exception(exception: Exception):
    """
    通用的 Access Token 錯誤處理函數。
    :param exception: 捕獲的異常
    """
    if isinstance(exception, AttributeError):
        capture_exception(exception)
        handle_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating the access token",
        )
    else:
        capture_exception(exception)
        handle_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

def handle_request_exception(e: Exception, context: str):
    """
    通用的請求錯誤處理函數，根據異常類型進行處理。
    :param e: 捕獲的異常
    :param context: 異常發生的上下文描述
    """
    capture_exception(e)
    logger.error(f"{context}: {str(e)}")

    if isinstance(e, Timeout):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The request timed out. Please try again later.",
        )
    elif isinstance(e, ConnectionError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A connection error occurred. Please try again later.",
        )
    elif isinstance(e, HTTPError):
        raise HTTPException(
            status_code=e.response.status_code,
            detail="An HTTP error occurred while processing the request.",
        )
    elif isinstance(e, RequestException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the necessities prices. Please try again later.",
        )
    elif isinstance(e, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while processing the API response. Please check your input.",
        )
    elif isinstance(e, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error occurred. Please check your input.",
        )
    elif isinstance(e, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred. Please try again later.",
        )
    elif isinstance(e, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated or username is missing.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
    

def handle_api_exception(e: Exception, context: str, status_code: int, detail: str):
    capture_exception(e)
    logger.error(f"{context}: {str(e)}")
    raise HTTPException(status_code=status_code, detail=detail)
