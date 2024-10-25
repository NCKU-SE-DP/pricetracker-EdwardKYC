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
from src.auth.database import (engine, Base  , SessionLocal , session_opener)
from src.auth.utils import (pwd_context , oauth2_scheme , verify_password , check_user_password_is_correct , _id_counter)
from src.auth.router import (login_for_access_token , create_user , read_usersname , read_news , read_user_news , 
                             search_news_articles , news_summary , upvote_article , toggle_upvote , get_necessities_prices)
from src.auth.schema import(UserAuthSchema , PromptRequest , NewsSumaryRequestSchema)
from openai import OpenAI
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

def add_news_article(news_article_data):
    """
    add new to db
    :param news_data: news info
    :return:
    """
    session = Session()
    session.add(NewsArticle(
        url=news_article_data["url"],
        title=news_article_data["title"],
        time=news_article_data["time"],
        content=" ".join(news_article_data["content"]),  # 將內容list轉換為字串
        summary=news_article_data["summary"],
        reason=news_article_data["reason"],
    ))
    session.commit()
    session.close()


def fetch_news_articles_by_keyword(search_term, is_initial=False):
    """
    Fetches news articles based on the search keyword.

    :param search_term: The search keyword.
    :param is_initial: Boolean flag indicating whether this is the initial fetch.
    :return: List of news articles.
    """
    all_news_data = []
    
    # Iterate pages to get more news data
    if is_initial:
        for page in range(1, 10):
            request_params = {
                "page": page,
                "id": f"search:{quote(search_term)}",
                "channelId": 2,
                "type": "searchword",
            }
            response = requests.get("https://udn.com/api/more", params=request_params)
            all_news_data.extend(response.json()["lists"])  # Append each page's news data without re-adding

    else:
        request_params = {
            "page": 1,
            "id": f"search:{quote(search_term)}",
            "channelId": 2,
            "type": "searchword",
        }
        response = requests.get("https://udn.com/api/more", params=request_params)
        all_news_data = response.json()["lists"]

    return all_news_data


def fetch_and_process_news(is_initial=False):
    """
    get new info

    :param is_initial:
    :return:
    """
    news_articles = fetch_news_articles_by_keyword("價格", is_initial=is_initial)

    # Iterate through each news article
    for article in news_articles:
        article_title = article["title"]
        relevance_check_prompt = [
            {
                "role": "system",
                "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            },
            {"role": "user", "content": f"{article_title}"},
        ]

        # Get AI evaluation on relevance of the news article title
        ai_response = OpenAI(api_key="xxx").chat.completions.create(
            model="gpt-3.5-turbo",
            messages=relevance_check_prompt,
        )
        relevance = ai_response.choices[0].message.content

        # If the relevance is high, fetch full article details and process
        if relevance == "high":
            response = requests.get(article["titleLink"])
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title and time from the article
            detailed_title = soup.find("h1", class_="article-content__title").text
            publication_time = soup.find("time", class_="article-content__time").text

            # Extract article content
            content_section = soup.find("section", class_="article-content__editor")
            content_paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            
            # Prepare detailed news data
            detailed_news_data = {
                "url": article["titleLink"],
                "title": detailed_title,
                "time": publication_time,
                "content": content_paragraphs,
            }

            # Generate summary and reason using AI
            summary_prompt = [
                {
                    "role": "system",
                    "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
                },
                {"role": "user", "content": " ".join(detailed_news_data["content"])},
            ]

            summary_completion = OpenAI(api_key="xxx").chat.completions.create(
                model="gpt-3.5-turbo",
                messages=summary_prompt,
            )
            summary_result = json.loads(summary_completion.choices[0].message.content)

            # Add summary and reason to detailed news data
            detailed_news_data["summary"] = summary_result["影響"]
            detailed_news_data["reason"] = summary_result["原因"]

            # Add the news article to the database
            add_news_article(detailed_news_data)

def authenticate_user_token(
    token = Depends(oauth2_scheme),
    db = Depends(session_opener)
):
    payload = jwt.decode(token, '1892dhianiandowqd0n', algorithms=["HS256"])
    return db.query(User).filter(User.username == payload.get("sub")).first()



def create_access_token(user_data, expires_delta=None):
    """create access token"""
    to_encode = user_data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, '1892dhianiandowqd0n', algorithm="HS256")
    return encoded_jwt

def get_article_upvote_details(article_id, uid, db):
    upvote_count = (
        db.query(user_news_association_table)
        .filter_by(news_articles_id=article_id)
        .count()
    )

    has_voted = False
    if uid:
        has_voted = (
            db.query(user_news_association_table)
            .filter_by(news_articles_id=article_id, user_id=uid)
            .first() is not None
        )

    return upvote_count, has_voted

def news_exists(article_id, db: Session):
    return db.query(NewsArticle).filter_by(id=article_id).first() is not None

