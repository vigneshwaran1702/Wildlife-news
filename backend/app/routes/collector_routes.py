from fastapi import APIRouter
from typing import List, Dict
from app.models.schemas import CollectorLog
from app.collectors.rss import RSSCollector
from app.collectors.tamil_news import TamilNewsCollector
from app.collectors.english_news import EnglishNewsCollector
from app.collectors.bing_collector import BingNewsCollector
from app.collectors.newsdata_collector import NewsDataCollector
from app.services.storage import db_storage

router = APIRouter(prefix="/api/collectors", tags=["Collectors"])

@router.get("/logs", response_model=List[CollectorLog])
def get_collector_logs():
    return db_storage.get_logs()

@router.post("/bing")
def trigger_bing_collector() -> Dict:
    bing_count = BingNewsCollector.scrape_latest()
    return {
        "status": "Success",
        "bing_scraped": bing_count
    }

@router.post("/newsdata")
def trigger_newsdata_collector() -> Dict:
    newsdata_count = NewsDataCollector.scrape_latest()
    return {
        "status": "Success",
        "newsdata_scraped": newsdata_count
    }

@router.post("/trigger")
def trigger_collectors() -> Dict:
    rss_count = RSSCollector.fetch_all()
    ta_count = TamilNewsCollector.scrape_latest()
    en_count = EnglishNewsCollector.scrape_latest()
    bing_count = BingNewsCollector.scrape_latest()
    newsdata_count = NewsDataCollector.scrape_latest()

    total_new = rss_count + ta_count + en_count + bing_count + newsdata_count
    return {
        "status": "Success",
        "total_new_articles": total_new,
        "rss_count": rss_count,
        "tamil_scraped": ta_count,
        "english_scraped": en_count,
        "bing_scraped": bing_count,
        "newsdata_scraped": newsdata_count
    }
