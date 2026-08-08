import feedparser
import httpx
from datetime import datetime
import uuid
from app.models.schemas import Article, CollectorLog
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
from app.services.storage import db_storage

class EnglishNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Fetches 100% live news directly from open source web RSS feeds for Tamil Nadu wildlife.
        """
        feed_url = "https://news.google.com/rss/search?q=Tamil+Nadu+wildlife+OR+elephant+OR+tiger+OR+leopard+OR+forest+department&hl=en-IN&gl=IN&ceid=IN:en"
        added = 0
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                title_en = entry.get("title", "")
                link = entry.get("link", "#")
                content_en = entry.get("summary", "") or entry.get("description", "") or title_en

                if not title_en:
                    continue

                # Strip HTML
                content_en = content_en.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip()

                # Filter strictly for Tamil Nadu + forest/wildlife relevance
                if not ArticleClassifier.is_tamil_nadu_relevant(title_en, content_en) or not ArticleClassifier.is_forest_or_wildlife_relevant(title_en, content_en):
                    continue

                existing = [a for a in db_storage.articles.values() if a.source_url == link or a.title_en == title_en]
                if existing:
                    continue

                # Source extraction
                source_name = "Google News - TN Division"
                if " - " in title_en:
                    parts = title_en.rsplit(" - ", 1)
                    title_en = parts[0]
                    source_name = parts[1]

                title_ta, content_ta = ArticleTranslator.translate_to_tamil(title_en, content_en)

                ai_meta = ArticleClassifier.classify(title_en, content_en)
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
                    source_name=source_name,
                    source_url=link,
                    published_at=datetime.now(),
                    tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
                    key_entities=ai_meta["key_entities"],
                    sentiment=ai_meta["sentiment"]
                )
                db_storage.add_article(art)
                added += 1

            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live English News Scraper",
                status="Success",
                articles_found=added,
                timestamp=datetime.now(),
                log_message=f"Fetched {added} live articles from TN open source media."
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
