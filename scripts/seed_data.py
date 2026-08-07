import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.collectors.rss import RSSCollector
from app.collectors.english_news import EnglishNewsCollector
from app.collectors.tamil_news import TamilNewsCollector

def seed_database():
    print("Fetching 100% LIVE open source news articles from Tamil Nadu wildlife RSS feeds & news outlets...")
    rss_count = RSSCollector.fetch_all()
    en_count = EnglishNewsCollector.scrape_latest()
    ta_count = TamilNewsCollector.scrape_latest()
    
    total = rss_count + en_count + ta_count
    print(f"Successfully fetched {total} LIVE articles (RSS: {rss_count}, English: {en_count}, Tamil: {ta_count}).")

if __name__ == "__main__":
    seed_database()
