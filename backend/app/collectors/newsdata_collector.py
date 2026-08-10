import os
import httpx
import logging
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.schemas import CollectorLog
from app.collectors.pipeline import ArticlePipeline
from app.services.storage import db_storage

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

class NewsDataCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Collects live news articles from NewsData.io API matching TN wildlife filters.
        Routes items through ArticlePipeline enforcing Date == TODAY filter.
        """
        api_key = os.getenv("NEWSDATA_API_KEY", NEWSDATA_API_KEY)
        total_added = 0
        log_msgs = []
        new_articles = []

        # Queries for NewsData.io
        queries = ["tamil nadu wildlife", "tamil nadu forest", "nilgiris elephant tiger"]

        for q in queries:
            try:
                if api_key:
                    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={q}&country=in&language=en,ta"
                else:
                    # Public search fallback endpoint
                    url = f"https://newsdata.io/api/1/news?q={q}&country=in"

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }

                res = httpx.get(url, headers=headers, timeout=12.0)
                if res.status_code != 200:
                    log_msgs.append(f"NewsData.io query '{q}' status {res.status_code}")
                    continue

                data = res.json()
                results = data.get("results", [])

                count = 0
                for item in results[:10]:
                    title = item.get("title", "").strip()
                    link = item.get("link", "#")
                    content = item.get("description", "") or item.get("content", "") or title
                    source_name = item.get("source_id", "NewsData.io").capitalize()

                    # Attach pubDate if available so pipeline can extract original publication date
                    pub_date_str = item.get("pubDate") or item.get("published_at") or datetime.now().isoformat()
                    raw_entry = {"published": pub_date_str, "pubDate": pub_date_str}

                    is_tamil = item.get("language") == "tamil" or item.get("language") == "ta"

                    article = ArticlePipeline.process_article(
                        raw_entry=raw_entry,
                        title=title,
                        content=content,
                        link=link,
                        source_name=source_name,
                        is_tamil=is_tamil,
                        batch_articles=new_articles
                    )

                    if article:
                        new_articles.append(article)
                        count += 1

                log_msgs.append(f"NewsData.io '{q}': {count} new today articles")

            except Exception as e:
                log_msgs.append(f"NewsData.io query '{q}' error: {str(e)}")

        if new_articles:
            db_storage.add_articles_batch(new_articles)
            total_added = len(new_articles)

        db_storage.add_log(CollectorLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            collector_name="NewsData.io Collector",
            status="Success" if total_added > 0 else "Info",
            articles_found=total_added,
            timestamp=datetime.now(),
            log_message="; ".join(log_msgs) if log_msgs else "No new articles found"
        ))

        return total_added

