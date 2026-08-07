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

@router.get("", response_model=List[Article])
def get_articles(
    category: Optional[str] = Query(None, description="Category filter"),
    district: Optional[str] = Query(None, description="District filter"),
    conflict_level: Optional[str] = Query(None, description="Conflict level filter"),
    species: Optional[str] = Query(None, description="Species filter"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    bookmarked_only: bool = Query(False, description="Show bookmarked only")
):
    return db_storage.get_articles(
        category=category,
        district=district,
        conflict_level=conflict_level,
        species=species,
        search=search,
        bookmarked_only=bookmarked_only
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
    
    title_ta = payload.title_ta
    content_ta = payload.content_ta

    if not title_ta or not content_ta:
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
        category=payload.category if payload.category != "General Wildlife" else ai_meta["category"],
        conflict_level=payload.conflict_level if payload.conflict_level != "Low" else ai_meta["conflict_level"],
        district=payload.district if payload.district != "Tamil Nadu" else ai_meta["district"],
        species=payload.species if payload.species else ai_meta["species"],
        source_name=payload.source_name,
        source_url=payload.source_url,
        published_at=payload.published_at or datetime.now(),
        tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
        key_entities=ai_meta["key_entities"],
        sentiment=ai_meta["sentiment"]
    )

    return db_storage.add_article(art)
