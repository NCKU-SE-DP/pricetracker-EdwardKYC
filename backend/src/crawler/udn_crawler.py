"""
UDN News Scraper Module

This module provides the UDNCrawler class for fetching, parsing, and saving news articles from the UDN website.
The class extends the NewsCrawlerBase and includes functionalities to search for news articles based on a search term,
parse the details of individual articles, and save them to a database using SQLAlchemy ORM.

Classes:
    UDNCrawler: A class to scrape news from UDN.

Exceptions:
    DomainMismatchException: Raised when the URL domain does not match the expected domain for the crawler.

Usage Example:
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)

UDNCrawler Methods:
    __init__(self, timeout: int = 5): Initializes the crawler with a default timeout for HTTP requests.
    startup(self, search_term: str) -> list[Headline]: Fetches news headlines for a given search term across multiple pages.
    get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]: Fetches news headlines for specified pages.
    _fetch_news(self, page: int, search_term: str) -> list[Headline]: Helper method to fetch news headlines for a specific page.
    _create_search_params(self, page: int, search_term: str): Creates the parameters for the search request.
    _perform_request(self, params: dict): Performs the HTTP request to fetch news data.
    _parse_headlines(response): Parses the response to extract headlines.
    parse(self, url: str) -> News: Parses a news article from a given URL.
    _extract_news(soup, url: str) -> News: Extracts news details from the BeautifulSoup object.
    save(self, news: News, db: Session): Saves a news article to the database.
    _commit_changes(db: Session): Commits the changes to the database with error handling.
"""
from sentry_sdk import capture_exception
import requests
from ..news.config import news_config
from ..news.models import NewsArticle
from requests import Response
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from sqlalchemy.orm import Session
from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from urllib.parse import quote
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        """
        Initializes the application by fetching news headlines for a given search term across multiple pages.
        This method is typically called at the beginning of the program when there is no data available,
        hence it fetches headlines from the first 10 pages.

        :param search_term: The term to search for in news headlines.
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        :rtype: list[Headline]
        """
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(
        self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:

        # Calculate the range of pages to fetch news from.
        # If 'page' is a tuple, unpack it and create a range representing those pages (inclusive).
        # If 'page' is an int, create a list containing only that single page number.
        # page_range = range(*page) if isinstance(page, tuple) else [page]
        page_range = range(page[0], page[1] + 1) if isinstance(page, tuple) else [page]

        headlines = []
        for page_num in page_range:
            headlines.extend(self._fetch_news(page=page_num, search_term=search_term))
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        params = self._create_search_params(page, search_term)
        response = self._perform_request(params=params)
        return self._parse_headlines(response)

    def _create_search_params(self, page: int, search_term: str) -> dict:
        request_params = {
            "page": page,
            "id": f"search:{quote(search_term)}",
            "channelId": 2,
            "type": "searchword",
        }
        return request_params

    def _perform_request(self, url: str | None = None, params: dict | None = None) -> Response:
        try:
            response = requests.get(url, params=params)
            
            # 如果回應的狀態碼表示錯誤，拋出HTTPError
            response.raise_for_status()
            
            return response

        except ValueError as e:
            # 捕獲URL未提供錯誤
            capture_exception(e)
            raise RuntimeError(f"Invalid input: {str(e)}")
        
        except Timeout as e:
            # 捕獲超時錯誤
            capture_exception(e)
            raise RuntimeError(f"Request to {url} timed out: {e}")
        
        except ConnectionError as e:
            # 捕獲連接錯誤
            capture_exception(e)
            raise RuntimeError(f"Connection error while requesting {url}: {e}")
        
        except HTTPError as e:
            # 捕獲HTTP錯誤，例如 404 或 500
            capture_exception(e)
            raise RuntimeError(f"HTTP error occurred during request to {url}: {e}")
        
        except RequestException as e:
            # 捕獲其他請求錯誤
            capture_exception(e)
            raise RuntimeError(f"Failed to perform request to {url}: {e}")
        
        except Exception as e:
            # 捕獲所有其他未預料的錯誤
            capture_exception(e)
            raise RuntimeError(f"An unexpected error occurred while requesting {url}: {e}")

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        try:
            data = response.json()
            headlines = []
            for item in data["lists"]:
                headlines.append(Headline(title=item["title"], url=item["titleLink"]))
            return headlines
        except (KeyError, ValueError) as e:
            print(e)

    def parse(self, url: str) -> News:
        response = self._perform_request(url=url)
        soup = BeautifulSoup(response.text, "html.parser")
        return self._extract_news(soup , url)

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        try:
            title = soup.find("h1", class_="article-content__title").text
            time = soup.find("time", class_="article-content__time").text
            content_section = soup.find("section", class_="article-content__editor")

            paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            content = " ".join(paragraphs)

            return News(
                url=url,
                title=title,
                time=time,
                content=content,
            )
        except AttributeError as e:
            print(f"Error extracting news details from {url}: {e}")
            raise

    def save(self, news: NewsWithSummary, db: Session):
        existing_news = db.query(NewsArticle).filter_by(url=news.url).first()
        if existing_news:
            print(f"News with URL {news.url} already exists. Skipping save.")
            return existing_news  # 返回现有记录，方便调用者处理

        new_article = NewsArticle(
            url=news.url,
            title=news.title,
            time=news.time,
            content=news.content,
            summary=news.summary,
            reason=news.reason,
        )

        db.add(new_article)
        try:
            self._commit_changes(db)
            return new_article  # 返回成功保存的对象
        except Exception as e:
            print(f"Error occurred while saving news: {e}")
            raise  # 抛出异常以便调用方处理
        finally:
            db.close()  # 确保连接始终被关闭

    @staticmethod
    def _commit_changes(db: Session):
        try:
            db.commit()
        except Exception as e:
            db.rollback()  # 回滚事务以防止锁定数据库
            raise e  # 抛出异常以便上层捕获
