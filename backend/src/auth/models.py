from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from fastapi import HTTPException, status

from ..database import Base
from ..database import user_news_association_table
from .constant import MAX_PASSWORD_SIZE, MAX_USERNAME_SIZE
from ..error import raise_validation_error
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
        if len(username) > MAX_USERNAME_SIZE:
            raise_validation_error("username", MAX_USERNAME_SIZE)

    @staticmethod
    def validate_password(password: str):
        if len(password) > MAX_PASSWORD_SIZE:
            raise_validation_error("password", MAX_PASSWORD_SIZE)