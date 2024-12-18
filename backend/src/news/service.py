import itertools
import requests
from urllib.parse import quote
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete
from ..crawler.udn_crawler import UDNCrawler    
from ..crawler.crawler_base import Headline 
from .models import NewsArticle
from ..auth.models import user_news_association_table
from .config import news_config
from ..ai_service.client import OpenAIClient
from ..ai_service.config import ai_config
from .utils import process_news_item, parse_summary_result
from ..database import SessionLocal
# Unique ID counter for generating temporary article IDs in memory.
article_id_counter = itertools.count(start=1000000)
openai_client = OpenAIClient(api_key=ai_config.OPEN_AI_KEY, model=ai_config.OPEN_AI_MODEL)
crawler = UDNCrawler()

def add_news_article(news_article_data):
    session = SessionLocal()
    crawler.save(news=news_article_data, db=session)

def add_news_article(news_article_data):
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
    if is_initial:
        return crawler.startup(search_term=search_term)
    else:
        return crawler.get_headline(search_term=search_term, page=1)
    
def fetch_and_process_news(is_initial=False):
    news_articles = fetch_news_articles_by_keyword("價格", is_initial=is_initial)
    for article in news_articles:
        article_title = article["title"]
        relevance = openai_client.evaluate_relevance(article_title)
        if relevance == "high":
            detailed_news = process_news_item(article)
            summary_result = openai_client.generate_summary(" ".join(detailed_news["content"]))
            detailed_news = parse_summary_result(summary_result)
            add_news_article(detailed_news)

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
    # if article_id == -1:  # 假設 -1 是無效的 ID
    #     raise ValueError("Invalid article ID.")
    

def toggle_upvote(article_id, uid, db_session):
    existing_upvote = db_session.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == article_id,
            user_news_association_table.c.user_id == uid,
        )
    ).scalar()

    if existing_upvote:
        delete_stmt = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == article_id,
            user_news_association_table.c.user_id == uid,
        )
        db_session.execute(delete_stmt)
        db_session.commit()
        return "Upvote removed"

    else:
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=article_id, user_id=uid
        )
        db_session.execute(insert_stmt)
        db_session.commit()
        return "Article upvoted"

def news_exists(article_id, db: Session):
    return db.query(NewsArticle).filter_by(id=article_id).first() is not None

