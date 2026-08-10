import feedparser
import httpx
from datetime import datetime
import uuid
from app.models.schemas import Article, CollectorLog
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
from app.services.storage import db_storage

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

class EnglishNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Fetches 100% live news directly from open source web RSS feeds for Tamil Nadu wildlife.
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

                if not title_en:
                    continue

                # Strip HTML
                content_en = content_en.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip()

                # Filter strictly for Tamil Nadu + forest/wildlife relevance
                if not ArticleClassifier.is_tamil_nadu_relevant(title_en, content_en) or not ArticleClassifier.is_forest_or_wildlife_relevant(title_en, content_en):
                    continue

                existing = [a for a in db_storage.articles.values() if a.source_url == link or a.title_en == title_en] or [a for a in new_articles if a.source_url == link or a.title_en == title_en]
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

                pub_dt = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub_dt = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pub_dt = None
                if not pub_dt:
                    pub_dt = datetime.now()

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
                    published_at=pub_dt,
                    tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
                    key_entities=ai_meta["key_entities"],
                    sentiment=ai_meta["sentiment"]
                )
                new_articles.append(art)

            if new_articles:
                db_storage.add_articles_batch(new_articles)

            added = len(new_articles)
            db_storage.add_log(CollectorLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                collector_name="Live English News Scraper",
                status="Success" if added > 0 else "Warning",
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
