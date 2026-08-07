import feedparser
import httpx
from datetime import datetime
import uuid

from app.models.schemas import Article, CollectorLog
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
from app.services.storage import db_storage

DEFAULT_RSS_FEEDS = [
    {"name": "The Hindu - Tamil Nadu", "url": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss", "lang": "en"},
    {"name": "The Hindu - Environment", "url": "https://www.thehindu.com/sci-tech/energy-and-environment/feeder/default.rss", "lang": "en"},
    {"name": "Mongabay India Conservation", "url": "https://india.mongabay.com/feed/", "lang": "en"},
    {"name": "Vikatan Environment", "url": "https://www.vikatan.com/rss/environment.xml", "lang": "ta"},
    {"name": "Dinamalar News", "url": "https://www.dinamalar.com/rss.asp", "lang": "ta"},
    {"name": "Indian Express Chennai", "url": "https://indianexpress.com/section/cities/chennai/feed/", "lang": "en"},
    {"name": "Down To Earth Wildlife", "url": "https://www.downtoearth.org.in/rss/wildlife-biodiversity", "lang": "en"}
]

class RSSCollector:
    @staticmethod
    def fetch_all() -> int:
        total_added = 0
        log_msgs = []

        for feed_info in DEFAULT_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_info["url"])
                count = 0
                for entry in feed.entries[:5]:  # Fetch latest 5 from each
                    title = entry.get("title", "")
                    content = entry.get("summary", "") or entry.get("description", "")
                    link = entry.get("link", "#")

                    if not title or not content:
                        continue

                    # Clean HTML tags from content
                    clean_content = content.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip()

                    # Check if relevant to Tamil Nadu state
                    if not ArticleClassifier.is_tamil_nadu_relevant(title, clean_content):
                        continue

                    # Check if already exists
                    existing = [a for a in db_storage.articles.values() if a.source_url == link]
                    if existing:
                        continue

                    is_tamil = feed_info["lang"] == "ta"

                    if is_tamil:
                        title_ta = title
                        content_ta = clean_content
                        title_en, content_en = ArticleTranslator.translate_to_english(title_ta, content_ta)
                    else:
                        title_en = title
                        content_en = clean_content
                        title_ta, content_ta = ArticleTranslator.translate_to_tamil(title_en, content_en)

                    # AI Classification
                    ai_meta = ArticleClassifier.classify(title_en, content_en)

                    # AI Summarization
                    sum_en = ArticleSummarizer.summarize_en(title_en, content_en)
                    sum_ta = ArticleSummarizer.summarize_ta(title_ta, content_ta)

                    art = Article(
                        id=f"art_{uuid.uuid4().hex[:8]}",
                        title_en=title_en,
                        title_ta=title_ta,
                        content_en=content_en,
                        content_ta=content_ta,
                        summary_en=sum_en,
                        summary_ta=sum_ta,
                        category=ai_meta["category"],
                        conflict_level=ai_meta["conflict_level"],
                        district=ai_meta["district"],
                        species=ai_meta["species"],
                        source_name=feed_info["name"],
                        source_url=link,
                        published_at=datetime.now(),
                        tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
                        key_entities=ai_meta["key_entities"],
                        sentiment=ai_meta["sentiment"]
                    )

                    db_storage.add_article(art)
                    count += 1
                    total_added += 1

                log_msgs.append(f"{feed_info['name']}: {count} new articles")

            except Exception as e:
                log_msgs.append(f"{feed_info['name']} Error: {str(e)}")

        db_storage.add_log(CollectorLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            collector_name="RSS Feeds Collector",
            status="Success" if total_added > 0 else "Warning",
            articles_found=total_added,
            timestamp=datetime.now(),
            log_message="; ".join(log_msgs)
        ))

        return total_added
