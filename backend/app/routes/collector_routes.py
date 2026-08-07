from fastapi import APIRouter
from typing import List, Dict
from app.models.schemas import CollectorLog
from app.collectors.rss import RSSCollector
from app.collectors.tamil_news import TamilNewsCollector
from app.collectors.english_news import EnglishNewsCollector
from app.services.storage import db_storage

router = APIRouter(prefix="/api/collectors", tags=["Collectors"])

@router.get("/logs", response_model=List[CollectorLog])
def get_collector_logs():
    return db_storage.get_logs()

@router.post("/trigger")
def trigger_collectors() -> Dict:
    rss_count = RSSCollector.fetch_all()
    ta_count = TamilNewsCollector.scrape_latest()
    en_count = EnglishNewsCollector.scrape_latest()

    total_new = rss_count + ta_count + en_count
    return {
        "status": "Success",
        "total_new_articles": total_new,
        "rss_count": rss_count,
        "tamil_scraped": ta_count,
        "english_scraped": en_count
    }
