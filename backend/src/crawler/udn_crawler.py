from .crawler_base import NewsCrawlerBase, Headline, News
from typing import List
from sqlalchemy.orm import Session

class UDNCrawler(NewsCrawlerBase):
    def __init__(self, news_website_url: str, news_website_news_child_urls: List[str]):
        self.news_website_url = news_website_url
        self.news_website_news_child_urls = news_website_news_child_urls

    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> List[Headline]:
        # 具體實現用於抓取 UDN 標題，這裡僅為占位範例
        return [
            Headline(title="Sample Title 1", url="https://udn.com/news/12345"),
            Headline(title="Sample Title 2", url="https://udn.com/news/67890"),
        ]

    def parse(self, url: str) -> News:
        # 假設從 UDN 網站解析新聞內容的具體邏輯
        return News(
            title="Sample Title",
            url=url,
            time="2024-11-26T12:00:00",
            content="This is the sample content of the article."
        )

    @staticmethod
    def save(news: News, db: Session | None):
        # 將數據存入數據庫的具體邏輯
        print(f"Saving news: {news.title} to the database.")
