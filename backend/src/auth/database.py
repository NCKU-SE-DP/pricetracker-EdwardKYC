import json
import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
import itertools
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
import requests
from fastapi import APIRouter, HTTPException, Query, Depends, status, FastAPI
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, AnyHttpUrl
from sqlalchemy import (Column, ForeignKey, Integer, String, Table, Text,create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from src.auth.model import (user_news_association_table , User , NewsArticle)
from src.auth.service import (add_news_article , fetch_news_articles_by_keyword , fetch_and_process_news , 
                              authenticate_user_token , create_access_token , get_article_upvote_details , news_exists)
from src.auth.utils import (pwd_context , oauth2_scheme , verify_password , check_user_password_is_correct , _id_counter)
from src.auth.router import (login_for_access_token , create_user , read_usersname , read_news , read_user_news , 
                             search_news_articles , news_summary , upvote_article , toggle_upvote , get_necessities_prices)
from src.auth.schema import(UserAuthSchema , PromptRequest , NewsSumaryRequestSchema)
from openai import OpenAI
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

Base = declarative_base()
engine = create_engine("sqlite:///news_database.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def session_opener():
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()
