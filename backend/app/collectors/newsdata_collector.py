import os
import httpx
import logging
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.schemas import Article, CollectorLog
from app.ai.classifier import ArticleClassifier
from app.ai.openai_service import OpenAIService
from app.services.storage import db_storage

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

class NewsDataCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Collects live news articles from NewsData.io API matching TN wildlife filters.
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

                    if not title or not link:
                        continue

                    # Filter TN and Wildlife relevance
                    if not ArticleClassifier.is_tamil_nadu_relevant(title, content) or not ArticleClassifier.is_forest_or_wildlife_relevant(title, content):
                        continue

                    # Deduplication
                    if any(a.source_url == link for a in db_storage.articles.values()) or any(a.source_url == link for a in new_articles):
                        continue

                    # AI processing
                    ai_res = OpenAIService.process_live_article(title, content, source_name)

                    art = Article(
                        id=f"art_{uuid.uuid4().hex[:8]}",
                        title_en=title,
                        title_ta=ai_res.get("title_ta", "") or title,
                        content_en=content,
                        content_ta=ai_res.get("content_ta", "") or content,
                        summary_en=ai_res.get("summary_en", ""),
                        summary_ta=ai_res.get("summary_ta", ""),
                        category=ai_res.get("category", "General Wildlife"),
                        conflict_level=ai_res.get("conflict_level", "Low"),
                        district=ai_res.get("district", "Tamil Nadu"),
                        species=ai_res.get("species", ["Wildlife"]),
                        source_name=source_name,
                        source_url=link,
                        published_at=datetime.now(),
                        tags=[ai_res.get("category", "General Wildlife"), ai_res.get("district", "Tamil Nadu")],
                        key_entities=ai_res.get("key_entities", None),
                        sentiment=ai_res.get("sentiment", "Neutral")
                    )
                    new_articles.append(art)
                    count += 1

                log_msgs.append(f"NewsData.io '{q}': {count} new articles")

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
