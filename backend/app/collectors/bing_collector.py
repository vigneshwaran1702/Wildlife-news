import feedparser
import httpx
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import uuid

from app.models.schemas import Article, CollectorLog
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
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
        """
        total_added = 0
        log_msgs = []
        new_articles = []

        for feed_info in BING_NEWS_QUERIES:
            name = feed_info["name"]
            url = feed_info["url"]
            try:
                try:
                    response = httpx.get(url, headers=HEADERS, timeout=15.0, follow_redirects=True)
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

                    if not title_en:
                        continue

                    # Clean HTML tags
                    clean_content = content_en.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip()

                    # Source extraction
                    source_name = "Bing News Media"
                    if " - " in title_en:
                        parts = title_en.rsplit(" - ", 1)
                        title_en = parts[0]
                        source_name = parts[1]

                    # Relevance filter
                    if not ArticleClassifier.is_tamil_nadu_relevant(title_en, clean_content) or not ArticleClassifier.is_forest_or_wildlife_relevant(title_en, clean_content):
                        continue

                    # Duplicate check against db_storage and new_articles
                    if any(a.source_url == link for a in db_storage.articles.values()) or any(a.source_url == link for a in new_articles):
                        continue

                    # Translate to Tamil
                    title_ta, content_ta = ArticleTranslator.translate_to_tamil(title_en, clean_content)

                    # AI Metadata & Summaries
                    ai_meta = ArticleClassifier.classify(title_en, clean_content)
                    sum_en = ArticleSummarizer.summarize_en(title_en, clean_content)
                    sum_ta = ArticleSummarizer.summarize_ta(title_ta, content_ta)

                    # Publication datetime in IST
                    pub_dt = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            utc_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                            pub_dt = utc_dt.astimezone(IST).replace(tzinfo=None)
                        except Exception:
                            pub_dt = None
                    if not pub_dt:
                        pub_dt = datetime.now()

                    art = Article(
                        id=f"art_{uuid.uuid4().hex[:8]}",
                        title_en=title_en,
                        title_ta=title_ta,
                        content_en=clean_content,
                        content_ta=content_ta,
                        summary_en=sum_en,
                        summary_ta=sum_ta,
                        category=ai_meta["category"],
                        conflict_level=ai_meta["conflict_level"],
                        district=ai_meta["district"],
                        species=ai_meta["species"],
                        source_name=source_name,
                        source_url=link,
                        published_at=pub_dt,
                        tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
                        key_entities=ai_meta["key_entities"],
                        sentiment=ai_meta["sentiment"]
                    )
                    new_articles.append(art)
                    count += 1

                log_msgs.append(f"{name}: {count} new articles")

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
