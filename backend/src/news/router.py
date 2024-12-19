import logging
from fastapi import APIRouter, Depends , HTTPException, status
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..crawler.udn_crawler import UDNCrawler    
from ..auth.service import authenticate_user_token
from ..database import session_opener
from .models import NewsArticle
from .schemas import PromptRequest, NewsSumaryRequestSchema, NewsSumaryCustomModelSchema
from ..ai_service.client import OpenAIClient , AnthropicClient
from .utils import process_news_item, parse_summary_result , convert_news_to_dict
from ..ai_service.config import ai_config
from .service import (
    article_id_counter,
    fetch_news_articles_by_keyword,
    get_article_upvote_details,
    toggle_upvote,
)
from ..logger.base import logger

openai_client = OpenAIClient(api_key=ai_config.OPEN_AI_KEY, model=ai_config.OPEN_AI_MODEL)
anthropic_client = AnthropicClient(api_key=ai_config.ANTHROPIC_API_KEY, model=ai_config.ANTHROPIC_MODEL)

router = APIRouter(
    prefix="/news",
    tags=["News"],
    responses={404: {"description": "Not found"}},
)
def get_ai_client(model: str):
    if model == "openai":
        return openai_client
    elif model == "anthropic":
        return anthropic_client
    else:
        raise ValueError("Invalid model specified. Choose 'openai' or 'anthropic'.")

@router.get("/news")
def fetch_news_with_upvote_details(db: Session = Depends(session_opener)):
    try:
        logger.info("Fetching all news articles with upvote details.")
        news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
        result = []
        for article in news:
            upvotes, upvoted = get_article_upvote_details(article.id, None, db)
            result.append(
                {"id": article.id, "title": article.title, "content": article.content, "upvotes": upvotes, "is_upvoted": upvoted}
            )
        logger.info(f"Successfully fetched {len(result)} news articles.")
        return result
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error fetching news articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching news articles. Please try again later.",
        )
@router.get("/user_news")
def get_user_specific_news(
    db: Session = Depends(session_opener),
    user = Depends(authenticate_user_token)
):
    try:
        logger.info(f"Fetching user-specific news for user: {user.username}")
        news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
        result = []
        for article in news:
            try:
                upvotes, upvoted = get_article_upvote_details(article.id, user.id, db)
            except Exception as e:
                capture_exception(e)
                logger.error(f"Error fetching upvote details for article {article.id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while fetching upvote details for the article.",
                )
            result.append(
                {
                    **article.__dict__,
                    "upvotes": upvotes,
                    "is_upvoted": upvoted,
                }
            )
        logger.info(f"Successfully fetched {len(result)} user-specific news articles.")
        return result
    except SQLAlchemyError as e:
        capture_exception(e)
        logger.error(f"SQLAlchemy error fetching news articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching news articles from the database. Please try again later.",
        )
    except Exception as e:
        capture_exception(e)
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching user-specific news. Please try again later.",
        )

@router.post("/search_news")
async def search_news_articles(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    
    # Step 1: 提取搜索關鍵字
    try:
        logger.info(f"Extracting search keywords from prompt: {prompt[:20]}...")  # 顯示提示的前20個字
        keywords = openai_client.extract_search_keywords(prompt)
        logger.info(f"Successfully extracted keywords: {keywords}")
    except Exception as e:
        capture_exception(e)
        logger.error(f"Failed to extract search keywords from prompt: {prompt}. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract search keywords from the prompt.",
        )
    
    # Step 2: 爬取新聞文章
    try:
        logger.info(f"Fetching news articles for keywords: {keywords}")
        crawler = UDNCrawler()
        news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
        logger.info(f"Successfully fetched {len(news_items)} news articles.")
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error fetching news articles for keywords: {keywords}. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching news articles. Please try again later.",
        )
    
    # Step 3: 處理每篇新聞文章
    for news in news_items:
        try:
            logger.debug(f"Parsing news article {news.url}")
            detailed_news = convert_news_to_dict(crawler.parse(news.url))
            detailed_news["id"] = next(article_id_counter)
            news_list.append(detailed_news)
            logger.info(f"Processed news article: {news.url}")
        except Exception as e:
            capture_exception(e)
            logger.error(f"Error processing news article {news.url}: {e}")
    
    # Step 4: 排序並返回結果
    try:
        sorted_news = sorted(news_list, key=lambda x: x["time"], reverse=True)
        logger.info(f"Successfully sorted {len(sorted_news)} news articles.")
        return sorted_news
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error sorting news articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sorting the news articles.",
        )
    
@router.post("/news_summary")
async def news_summary(
    payload: NewsSumaryRequestSchema, user=Depends(authenticate_user_token)
):
    try:
        logger.info(f"Received news summary request for user: {user.username}")
        logger.debug(f"Generating summary for content: {payload.content[:100]}...")  # 顯示文章內容的前100個字
        result = openai_client.generate_summary(payload.content)
        logger.info("News summary generated successfully.")
        return parse_summary_result(result)
    
    except Exception as e:
        capture_exception(e)
        logger.error(f"Error generating news summary for user {user.username}. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the news summary. Please try again later.",
        )


@router.post("/news_summary_custom_model")
async def news_summary_custom_model(
        payload: NewsSumaryCustomModelSchema, 
        user=Depends(authenticate_user_token)
):
    ai_client = get_ai_client(payload.ai_model)
    
    result = ai_client.generate_summary(payload.content)
    
    return parse_summary_result(result)

@router.post("/news_summary_custom_model")
async def news_summary_custom_model(
        payload: NewsSumaryCustomModelSchema, 
        user=Depends(authenticate_user_token)
):
    ai_client = get_ai_client(payload.ai_model)
    
    result = ai_client.generate_summary(payload.content)
    
    return parse_summary_result(result)

@router.post("/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        user=Depends(authenticate_user_token),
):
    message = toggle_upvote(article_id, user.id, db)
    return {"message": message}

