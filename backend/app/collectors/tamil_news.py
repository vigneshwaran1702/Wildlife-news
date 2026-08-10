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

class TamilNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Fetches live Tamil language news directly from open source media feeds.
        Routes entries through ArticlePipeline enforcing Date == TODAY filter.
        """
        feed_url = "https://news.google.com/rss/search?q=%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D%E0%AE%A5%E0%AE%BE%E0%AE%9F%E0%AF%8D%E0%AE%9F%E0%AF%88+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88+OR+%E0%AE%AA%E0%AF%81%E0%AE%B2%E0%AE%BF&hl=ta&gl=IN&ceid=IN:ta"
        new_articles = []
        try:
            try:
                response = httpx.get(feed_url, headers=HEADERS, timeout=15.0, follow_redirects=True)
                if response.status_code != 200:
                    db_storage.add_log(CollectorLog(
                        id=f"log_{uuid.uuid4().hex[:8]}",
                        collector_name="Live Tamil Media Scraper",
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
                    collector_name="Live Tamil Media Scraper",
                    status="Error",
                    articles_found=0,
                    timestamp=datetime.now(),
                    log_message=f"HTTP fetch error: {str(http_err)}"
                ))
                return 0

            feed = feedparser.parse(feed_content)
            for entry in feed.entries[:10]:
                title_ta = entry.get("title", "")
                link = entry.get("link", "#")
                content_ta = entry.get("summary", "") or entry.get("description", "") or title_ta

                source_name = "Tamil News Outlet"
                if " - " in title_ta:
                    parts = title_ta.rsplit(" - ", 1)
                    source_name = parts[1].strip()

                article = ArticlePipeline.process_article(
                    raw_entry=entry,
                    title=title_ta,
                    content=content_ta,
                    link=link,
                    source_name=source_name,
                    is_tamil=True,
                    batch_articles=new_articles
                )

                if article:
                    new_articles.append(article)

            if new_articles:
                db_storage.add_articles_batch(new_articles)

            added = len(new_articles)
            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live Tamil Media Scraper",
                status="Success" if added > 0 else "Warning",
                articles_found=added,
                timestamp=datetime.now(),
                log_message=f"Scraped {added} live Tamil articles matching today's date."
            ))
        except Exception as e:
            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live Tamil Media Scraper",
                status="Error",
                articles_found=0,
                timestamp=datetime.now(),
                log_message=f"Scraper error: {str(e)}"
            ))

        return added

