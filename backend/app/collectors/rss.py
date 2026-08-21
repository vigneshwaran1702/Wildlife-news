import feedparser
import httpx
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import uuid

IST = ZoneInfo("Asia/Kolkata")

from app.models.schemas import Article, CollectorLog
from app.collectors.pipeline import ArticlePipeline
from app.services.storage import db_storage
from app.collectors.html_utils import clean_html

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

DEFAULT_RSS_FEEDS = [
    # --- TAMIL CHANNELS & NEWSPAPERS ---
    # 1. தினத் தந்தி (Daily Thanthi)
    {"name": "Dina Thanthi (தினத்தந்தி)", "url": "https://news.google.com/rss/search?q=site:dailythanthi.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88+OR+%E0%AE%AA%E0%AF%81%E0%AE%B2%E0%AE%BF&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 2. தினமலர் (Dinamalar)
    {"name": "Dinamalar (தினமலர்)", "url": "https://www.dinamalar.com/rss.asp", "lang": "ta"},
    # 3. தினமணி (Dinamani)
    {"name": "Dinamani (தினமணி)", "url": "https://news.google.com/rss/search?q=site:dinamani.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%95%E0%AE%BE%E0%AE%9F%E0%AF%8D%E0%AE%9F%E0%AF%8B+%E0%AE%A4%E0%AF%80&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 4. தமிழ் இந்து (Tamil Hindu / Hindu Tamil Thisai)
    {"name": "Hindu Tamil Thisai (தமிழ் இந்து)", "url": "https://news.google.com/rss/search?q=site:hindutamil.in+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 5. நியூஸ்18 தமிழ் (News18 Tamil)
    {"name": "News18 Tamil (நியூஸ்18 தமிழ்)", "url": "https://news.google.com/rss/search?q=site:tamil.news18.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 6. தந்தி TV (Thanthi TV)
    {"name": "Thanthi TV (தந்தி TV)", "url": "https://news.google.com/rss/search?q=site:thanthitv.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 7. Puthiya Thalaimurai (புதிய தலைமுறை)
    {"name": "Puthiya Thalaimurai (புதிய தலைமுறை)", "url": "https://news.google.com/rss/search?q=site:puthiyathalaimurai.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 8. Polimer News (பாலிமர் நியூஸ்)
    {"name": "Polimer News (பாலிமர் நியூஸ்)", "url": "https://news.google.com/rss/search?q=site:polimernews.com+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%B5%E0%AE%B9%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},
    # 9. News7 Tamil (நியூஸ்7 தமிழ்)
    {"name": "News7 Tamil (நியூஸ்7 தமிழ்)", "url": "https://news.google.com/rss/search?q=site:news7tamil.live+%E0%AE%B5%E0%AE%A9%E0%AE%A4%E0%AF%88%E0%AE%A4%E0%AF%81%E0%AE%B0%E0%AF%8D%E0%AE%AE%E0%AF%88+OR+%E0%AE%AF%E0%AE%BE%E0%AE%A9%E0%AF%88&hl=ta&gl=IN&ceid=IN:ta", "lang": "ta"},

    # --- ENGLISH CHANNELS & NEWSPAPERS ---
    # 10. The Hindu (Direct Feeds & Google Search)
    {"name": "The Hindu (TN Direct)", "url": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss", "lang": "en"},
    {"name": "The Hindu (Environment Direct)", "url": "https://www.thehindu.com/sci-tech/energy-and-environment/feeder/default.rss", "lang": "en"},
    {"name": "The Hindu (Google Search)", "url": "https://news.google.com/rss/search?q=site:thehindu.com+Tamil+Nadu+wildlife+OR+forest+department+OR+elephant+OR+tiger&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 11. The New Indian Express (Google Search)
    {"name": "The New Indian Express", "url": "https://news.google.com/rss/search?q=site:newindianexpress.com+Tamil+Nadu+wildlife+OR+forest+department+OR+poaching+OR+rescue&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 12. Times of India (Direct & Google Search)
    {"name": "Times of India (Chennai Direct)", "url": "https://timesofindia.indiatimes.com/rssfeeds/2950623.cms", "lang": "en"},
    {"name": "Times of India (Google Search)", "url": "https://news.google.com/rss/search?q=site:timesofindia.indiatimes.com+Tamil+Nadu+wildlife+OR+forest+department+OR+sanctuary&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 13. DT Next (Direct & Google Search)
    {"name": "DT Next (Direct)", "url": "https://www.dtnext.in/feed", "lang": "en"},
    {"name": "DT Next (Google Search)", "url": "https://news.google.com/rss/search?q=site:dtnext.in+wildlife+OR+forest+department+OR+elephant+OR+tiger&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 14. Deccan Chronicle
    {"name": "Deccan Chronicle", "url": "https://news.google.com/rss/search?q=site:deccanchronicle.com+Tamil+Nadu+wildlife+OR+forest+department&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 15. The News Minute
    {"name": "The News Minute", "url": "https://news.google.com/rss/search?q=site:thenewsminute.com+Tamil+Nadu+wildlife+OR+forest+department+OR+elephant&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 16. India Today
    {"name": "India Today", "url": "https://news.google.com/rss/search?q=site:indiatoday.in+Tamil+Nadu+wildlife+OR+forest+department&hl=en-IN&gl=IN&ceid=IN:en", "lang": "en"},
    # 17. The Indian Express (Direct Feed)
    {"name": "The Indian Express (Chennai Direct)", "url": "https://indianexpress.com/section/cities/chennai/feed/", "lang": "en"},

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
        new_articles = []

        for feed_info in DEFAULT_RSS_FEEDS:
            name = feed_info["name"]
            url = feed_info["url"]
            try:
                try:
                    response = httpx.get(url, headers=HEADERS, timeout=4.0, follow_redirects=True)
                    if response.status_code != 200:
                        log_msg = f"Google blocked request: status {response.status_code}" if "google.com" in url else f"Request blocked: status {response.status_code}"
                        log_msgs.append(f"{name}: {log_msg}")
                        continue
                    feed_content = response.text
                except Exception as http_err:
                    log_msgs.append(f"{name} HTTP Fetch Error: {str(http_err)}")
                    continue

                feed = feedparser.parse(feed_content)
                count = 0
                for entry in feed.entries[:10]:
                    title = entry.get("title", "")
                    content = clean_html(entry.get("summary", "") or entry.get("description", ""))
                    link = entry.get("link", "#")

                    is_tamil = feed_info["lang"] == "ta"

                    # Route through strict ArticlePipeline (Date == TODAY -> TN Location -> Forest/Wildlife -> Duplicate -> Source -> DB)
                    article = ArticlePipeline.process_article(
                        raw_entry=entry,
                        title=title,
                        content=content,
                        link=link,
                        source_name=name,
                        is_tamil=is_tamil,
                        batch_articles=new_articles
                    )

                    if article:
                        new_articles.append(article)
                        count += 1

                log_msgs.append(f"{name}: {count} new today articles")

            except Exception as e:
                log_msgs.append(f"{name} Error: {str(e)}")

        if new_articles:
            db_storage.add_articles_batch(new_articles)
            total_added = len(new_articles)

        db_storage.add_log(CollectorLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            collector_name="RSS Feeds Collector",
            status="Success" if total_added > 0 else "Warning",
            articles_found=total_added,
            timestamp=datetime.now(),
            log_message="; ".join(log_msgs)
        ))

        return total_added

