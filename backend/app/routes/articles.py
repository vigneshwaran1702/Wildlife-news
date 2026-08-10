from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.models.schemas import Article, ArticleCreate
from app.services.storage import db_storage
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/articles", tags=["Articles"])

from app.collectors.bing_collector import BingNewsCollector
from app.collectors.pipeline import ArticlePipeline

@router.get("", response_model=List[Article])
def get_articles(
    category: Optional[str] = Query(None, description="Category filter"),
    district: Optional[str] = Query(None, description="District filter"),
    conflict_level: Optional[str] = Query(None, description="Conflict level filter"),
    species: Optional[str] = Query(None, description="Species filter"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    bookmarked_only: bool = Query(False, description="Show bookmarked only"),
    todays_only: bool = Query(False, description="Show today's news only"),
    date_status: Optional[str] = Query(None, description="Date status filter: TODAY, YESTERDAY, OLD"),
    refresh_live: bool = Query(False, description="Fetch fresh live online news directly")
):
    if refresh_live:
        try:
            BingNewsCollector.scrape_latest()
        except Exception as e:
            pass

    return db_storage.get_articles(
        category=category,
        district=district,
        conflict_level=conflict_level,
        species=species,
        search=search,
        bookmarked_only=bookmarked_only,
        todays_only=todays_only,
        date_status=date_status
    )

@router.get("/{article_id}", response_model=Article)
def get_article(article_id: str):
    article = db_storage.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.views_count += 1
    db_storage.save_data()
    return article

@router.post("/bookmark/{article_id}", response_model=Article)
def toggle_bookmark(article_id: str):
    article = db_storage.toggle_bookmark(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("", response_model=Article)
def create_article(payload: ArticleCreate):
    title_en = payload.title_en
    content_en = payload.content_en
    source_url = payload.source_url or "https://news.google.com"

    # Enforce ArticlePipeline (Extract date -> Date == TODAY -> TN Location -> Forest/Wildlife -> Duplicate -> Source -> DB)
    raw_entry = {"published_at": payload.published_at or datetime.now()}
    art = ArticlePipeline.process_article(
        raw_entry=raw_entry,
        title=title_en,
        content=content_en,
        link=source_url,
        source_name=payload.source_name or "Manual Submission",
        is_tamil=False
    )

    if not art:
        raise HTTPException(
            status_code=400,
            detail="Article REJECTED by Pipeline: Must have original date == TODAY, be relevant to Tamil Nadu, and focus on Forest/Wildlife."
        )

    # Apply optional user overrides
    if payload.category and payload.category != "General Wildlife":
        art.category = payload.category
    if payload.district and payload.district != "Tamil Nadu":
        art.district = payload.district
    if payload.conflict_level and payload.conflict_level != "Low":
        art.conflict_level = payload.conflict_level
    if payload.species:
        art.species = payload.species

    return db_storage.add_article(art)

