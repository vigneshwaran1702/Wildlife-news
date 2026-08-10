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
HEADERS = {"User-Agent": USER_AGENT}

class EnglishNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Fetches live English news directly from open source media feeds for Tamil Nadu wildlife.
        Routes entries through ArticlePipeline enforcing Date == TODAY filter.
        """
        feed_url = "https://news.google.com/rss/search?q=Tamil+Nadu+wildlife+OR+forest+department+OR+forest+fire+OR+wildlife+crime+OR+protected+area+OR+rescue+OR+seizure+OR+encroachment+OR+forest+policy&hl=en-IN&gl=IN&ceid=IN:en"
        new_articles = []
        try:
            try:
                response = httpx.get(feed_url, headers=HEADERS, timeout=15.0, follow_redirects=True)
                if response.status_code != 200:
                    db_storage.add_log(CollectorLog(
                        id=f"log_{uuid.uuid4().hex[:8]}",
                        collector_name="Live English News Scraper",
                        status="Warning",
                        articles_found=0,
                        timestamp=datetime.now(),
                        log_message=f"Google blocked request: status {response.status_code}"
                    ))
                    return 0
                feed_content = response.text
            except Exception as http_err:
                db_storage.add_log(CollectorLog(
                    id=f"log_{uuid.uuid4().hex[:8]}",
                    collector_name="Live English News Scraper",
                    status="Error",
                    articles_found=0,
                    timestamp=datetime.now(),
                    log_message=f"Fetch error: {str(http_err)}"
                ))
                return 0

            feed = feedparser.parse(feed_content)
            for entry in feed.entries[:10]:
                title_en = entry.get("title", "")
                link = entry.get("link", "#")
                content_en = entry.get("summary", "") or entry.get("description", "") or title_en

                source_name = "Google News - TN Division"
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

            if new_articles:
                db_storage.add_articles_batch(new_articles)

            added = len(new_articles)
            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live English News Scraper",
                status="Success" if added > 0 else "Warning",
                articles_found=added,
                timestamp=datetime.now(),
                log_message=f"Fetched {added} live articles matching today's date from TN media."
            ))
        except Exception as e:
            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live English News Scraper",
                status="Error",
                articles_found=0,
                timestamp=datetime.now(),
                log_message=f"Fetch error: {str(e)}"
            ))

        return added

