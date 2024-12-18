from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from fastapi import HTTPException, status

from ..database import Base
from ..database import user_news_association_table
from .constant import MAX_PASSWORD_SIZE, MAX_USERNAME_SIZE

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Ensure that the length is within the specified max size
    username = Column(String(MAX_USERNAME_SIZE), unique=True, nullable=False)
    hashed_password = Column(String(MAX_PASSWORD_SIZE), nullable=False)
    
    upvoted_news = relationship(
        "NewsArticle",
        secondary=user_news_association_table,
        back_populates="upvoted_by_users",
    )
    
    @staticmethod
    def validate_username(username: str):
        # If the username exceeds the max length, raise an exception
        if len(username) > MAX_USERNAME_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username exceeds the maximum length of {MAX_USERNAME_SIZE} characters."
            )

    @staticmethod
    def validate_password(password: str):
        # If the password exceeds the max length, raise an exception
        if len(password) > MAX_PASSWORD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password exceeds the maximum length of {MAX_PASSWORD_SIZE} characters."
            )