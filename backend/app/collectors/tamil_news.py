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

class TamilNewsCollector:
    @staticmethod
    def scrape_latest() -> int:
        """
        Fetches 100% live Tamil language news directly from open source media feeds.
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

                if not title_ta:
                    continue

                content_ta = content_ta.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip()

                source_name = "Tamil News Outlet"
                if " - " in title_ta:
                    parts = title_ta.rsplit(" - ", 1)
                    title_ta = parts[0]
                    source_name = parts[1]

                title_en, content_en = ArticleTranslator.translate_to_english(title_ta, content_ta)

                # Filter strictly for Tamil Nadu + forest/wildlife relevance
                if not ArticleClassifier.is_tamil_nadu_relevant(title_en, content_en) or not ArticleClassifier.is_forest_or_wildlife_relevant(title_en, content_en):
                    continue

                existing = [a for a in db_storage.articles.values() if a.source_url == link or a.title_ta == title_ta] or [a for a in new_articles if a.source_url == link or a.title_ta == title_ta]
                if existing:
                    continue

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
                collector_name="Live Tamil Media Scraper",
                status="Success" if added > 0 else "Warning",
                articles_found=added,
                timestamp=datetime.now(),
                log_message=f"Scraped {added} live Tamil articles."
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
