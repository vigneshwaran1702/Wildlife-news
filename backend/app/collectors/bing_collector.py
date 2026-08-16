import feedparser
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

from app.models.schemas import CollectorLog
from app.collectors.pipeline import ArticlePipeline
from app.services.storage import db_storage

IST = ZoneInfo("Asia/Kolkata")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9"
}

BING_NEWS_QUERIES = [
    {"name": "Bing - TN Wildlife", "url": "https://www.bing.com/news/search?q=Tamil+Nadu+wildlife&format=rss"},
    {"name": "Bing - TN Forest Dept", "url": "https://www.bing.com/news/search?q=Tamil+Nadu+forest+department&format=rss"},
    {"name": "Bing - Nilgiris Wildlife", "url": "https://www.bing.com/news/search?q=Nilgiris+elephant+tiger+wildlife&format=rss"},
    {"name": "Bing - TN Rescue & Conflict", "url": "https://www.bing.com/news/search?q=Tamil+Nadu+wildlife+conflict+rescue&format=rss"},
    {"name": "Bing - Tiger Reserves TN", "url": "https://www.bing.com/news/search?q=Mudumalai+Anamalai+Sathyamangalam+wildlife&format=rss"}
]

class BingNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Actively collects live daily news articles from Bing News RSS feeds matching TN wildlife filters.
        Routes entries through ArticlePipeline enforcing Date == TODAY filter.
        """
        total_added = 0
        log_msgs = []
        new_articles = []

        for feed_info in BING_NEWS_QUERIES:
            name = feed_info["name"]
            url = feed_info["url"]
            try:
                try:
                    response = httpx.get(url, headers=HEADERS, timeout=4.0, follow_redirects=True)
                    if response.status_code != 200:
                        log_msgs.append(f"{name}: Bing request blocked (status {response.status_code})")
                        continue
                    feed_content = response.text
                except Exception as http_err:
                    log_msgs.append(f"{name} HTTP fetch error: {str(http_err)}")
                    continue

                feed = feedparser.parse(feed_content)
                count = 0
                for entry in feed.entries[:10]:
                    title_en = entry.get("title", "")
                    link = entry.get("link", "#")
                    content_en = entry.get("summary", "") or entry.get("description", "") or title_en

                    source_name = "Bing News Media"
                    if " - " in title_en:
                        parts = title_en.rsplit(" - ", 1)
                        source_name = parts[1].strip()

                    article = ArticlePipeline.process_article(
                        raw_entry=entry,
                        title=title_en,
                        content=content_en,
                        link=link,
                        source_name=source_name,
                        is_tamil=False,
                        batch_articles=new_articles
                    )

                    if article:
                        new_articles.append(article)
                        count += 1

                log_msgs.append(f"{name}: {count} new today articles")

            except Exception as e:
                log_msgs.append(f"{name} Error: {str(e)}")

        if new_articles:
            db_storage.add_articles_batch(new_articles)
            total_added = len(new_articles)

        db_storage.add_log(CollectorLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            collector_name="Bing Live News Collector",
            status="Success" if total_added > 0 else "Warning",
            articles_found=total_added,
            timestamp=datetime.now(),
            log_message="; ".join(log_msgs)
        ))

        return total_added

