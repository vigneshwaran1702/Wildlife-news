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
    # --- TAMIL CHANNELS & NEWSPAPERS ---
    # 1. தினத் தந்தி (Daily Thanthi)
    {"name": "Dina Thanthi (தினத்தந்தி)", "url": "https://news.google.com/rss/search?q=site:dailythanthi.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88+OR+%E0%AE%AA%E0%AF%81%E0%AE%B2%E0%AE%BF&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 2. தினமலர் (Dinamalar)
    {"name": "Dinamalar (தினமலர்)", "url": "https://www.dinamalar.com/rss.asp", "lang": "ta"},
    # 3. தினமணி (Dinamani)
    {"name": "Dinamani (தினமணி)", "url": "https://news.google.com/rss/search?q=site:dinamani.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%95%E0%AE%BE%E0%AE%9F%E0%AF%8D%E0%AE%9F%E0%AF%81+%E0%AE%A4%E0%AF%80&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 4. தமிழ் இந்து (Tamil Hindu / Hindu Tamil Thisai)
    {"name": "Hindu Tamil Thisai (தமிழ் இந்து)", "url": "https://news.google.com/rss/search?q=site:hindutamil.in+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 5. நியூஸ்18 தமிழ் (News18 Tamil)
    {"name": "News18 Tamil (நியூஸ்18 தமிழ்)", "url": "https://news.google.com/rss/search?q=site:tamil.news18.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 6. தந்தி TV (Thanthi TV)
    {"name": "Thanthi TV (தந்தி TV)", "url": "https://news.google.com/rss/search?q=site:thanthitv.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 7. Puthiya Thalaimurai (புதிய தலைமுறை)
    {"name": "Puthiya Thalaimurai (புதிய தலைமுறை)", "url": "https://news.google.com/rss/search?q=site:puthiyathalaimurai.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 8. Polimer News (பாலிமர் நியூஸ்)
    {"name": "Polimer News (பாலிமர் நியூஸ்)", "url": "https://news.google.com/rss/search?q=site:polimernews.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 9. News7 Tamil (நியூஸ்7 தமிழ்)
    {"name": "News7 Tamil (நியூஸ்7 தமிழ்)", "url": "https://news.google.com/rss/search?q=site:news7tamil.live+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},

    # --- ENGLISH CHANNELS & NEWSPAPERS ---
    # 10. The Hindu
    {"name": "The Hindu", "url": "https://news.google.com/rss/search?q=site:thehindu.com+Tamil+Nadu+wildlife+OR+forest+department+OR+elephant+OR+tiger&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 11. The New Indian Express
    {"name": "The New Indian Express", "url": "https://news.google.com/rss/search?q=site:newindianexpress.com+Tamil+Nadu+wildlife+OR+forest+department+OR+poaching+OR+rescue&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 12. Times of India
    {"name": "Times of India", "url": "https://news.google.com/rss/search?q=site:timesofindia.indiatimes.com+Tamil+Nadu+wildlife+OR+forest+department+OR+sanctuary&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 13. DT Next
    {"name": "DT Next", "url": "https://news.google.com/rss/search?q=site:dtnext.in+wildlife+OR+forest+department+OR+elephant+OR+tiger&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 14. Deccan Chronicle
    {"name": "Deccan Chronicle", "url": "https://news.google.com/rss/search?q=site:deccanchronicle.com+Tamil+Nadu+wildlife+OR+forest+department&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 15. The News Minute
    {"name": "The News Minute", "url": "https://news.google.com/rss/search?q=site:thenewsminute.com+Tamil+Nadu+wildlife+OR+forest+department+OR+elephant&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 16. India Today
    {"name": "India Today", "url": "https://news.google.com/rss/search?q=site:indiatoday.in+Tamil+Nadu+wildlife+OR+forest+department&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 17. The Indian Express
    {"name": "The Indian Express", "url": "https://indianexpress.com/section/cities/chennai/feed/", "lang": "en"},

    # --- OFFICIAL GOVERNMENT & FOREST SOURCES ---
    # 18. Tamil Nadu Forest Department
    {"name": "Tamil Nadu Forest Dept Official", "url": "https://news.google.com/rss/search?q=Tamil+Nadu+Forest+Department+press+release+OR+notification+OR+wildlife&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 19. Tamil Nadu Government Press Releases
    {"name": "TN Govt Press Releases", "url": "https://news.google.com/rss/search?q=Tamil+Nadu+government+forest+OR+wildlife+release&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 20. PIB Chennai
    {"name": "PIB Chennai", "url": "https://news.google.com/rss/search?q=PIB+Chennai+forest+OR+wildlife+OR+environment&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 21. Project Tiger / NTCA
    {"name": "Project Tiger / NTCA", "url": "https://news.google.com/rss/search?q=NTCA+National+Tiger+Conservation+Authority+Tamil+Nadu+OR+Mudumalai+OR+Sathyamangalam+OR+Anamalai+OR+KMTR&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 22. MoEFCC (Ministry of Environment, Forest & Climate Change)
    {"name": "MoEFCC India", "url": "https://news.google.com/rss/search?q=MoEFCC+Ministry+of+Environment+Forest+Tamil+Nadu+wildlife&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"}
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

                    # Check if relevant to Tamil Nadu + forest/wildlife news
                    if not ArticleClassifier.is_tamil_nadu_relevant(title, clean_content) or not ArticleClassifier.is_forest_or_wildlife_relevant(title, clean_content):
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
