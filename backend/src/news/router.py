from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
    """
    Fetch all news articles with their upvote details.

    :param db: Database session dependency for querying news articles.
    :return: A list of news articles with upvote count and upvoted status.
    """
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, None, db)
        result.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
        )
    return result

@router.get("/user_news")
def get_user_specific_news(
    db: Session = Depends(session_opener),
    user = Depends(authenticate_user_token)
):
    """
    Fetch news articles specific to the authenticated user.

    :param db: Database session dependency for querying news articles.
    :param user: Authenticated user dependency for user-specific data.
    :return: A list of news articles with upvote count and the user's upvoted status.
    """
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, user.id, db)
        result.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )
    return result

@router.post("/search_news")
async def search_news_articles(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    keywords = openai_client.extract_search_keywords(prompt)
    crawler = UDNCrawler()
    news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
    for news in news_items:
        try:
            abc = crawler.parse(news.url)
            detailed_news = convert_news_to_dict(crawler.parse(news.url))
            detailed_news["id"] = next(article_id_counter)
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)

@router.post("/news_summary")
async def news_summary(
        payload: NewsSumaryRequestSchema, user=Depends(authenticate_user_token)
):
    result = openai_client.generate_summary(payload.content)
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