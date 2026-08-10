import email.utils
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
import uuid
import logging

from app.models.schemas import Article
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
from app.ai.openai_service import OpenAIService
from app.services.storage import db_storage

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")

def parse_entry_datetime(entry: Any) -> Optional[datetime]:
    """
    Extracts original publication date/time from feed entry or metadata object.
    Converts to Asia/Kolkata (IST) timezone.
    """
    if isinstance(entry, dict):
        item = entry
    else:
        item = getattr(entry, '__dict__', {})

    # 1. feedparser published_parsed / updated_parsed
    published_parsed = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None) or item.get('published_parsed') or item.get('updated_parsed')
    if published_parsed:
        try:
            utc_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            return utc_dt.astimezone(IST).replace(tzinfo=None)
        except Exception:
            pass

    # 2. String timestamp parsing
    pub_str = getattr(entry, 'published', None) or getattr(entry, 'pubDate', None) or getattr(entry, 'updated', None) or item.get('published') or item.get('pubDate') or item.get('updated') or item.get('published_at') or item.get('pubdate')
    if pub_str and isinstance(pub_str, str):
        try:
            dt = email.utils.parsedate_to_datetime(pub_str)
            if dt:
                return dt.astimezone(IST).replace(tzinfo=None)
        except Exception:
            pass
        try:
            dt = datetime.fromisoformat(pub_str)
            if dt.tzinfo:
                return dt.astimezone(IST).replace(tzinfo=None)
            return dt
        except Exception:
            pass

    # 3. Direct datetime object
    pub_obj = item.get('published_at') or getattr(entry, 'published_at', None)
    if isinstance(pub_obj, datetime):
        if pub_obj.tzinfo:
            return pub_obj.astimezone(IST).replace(tzinfo=None)
        return pub_obj

    return None


class ArticlePipeline:
    """
    Enforces strict Article Ingestion Flowchart:
    Open source article
      ↓
    Extract ORIGINAL publication date/time
      ↓
    DATE FILTER: Is ORIGINAL article date today's date?
      │ NO  => REJECT
      ↓ YES
    LOCATION FILTER: Tamil Nadu related?
      │ NO  => REJECT
      ↓ YES
    TOPIC FILTER: Forest / Wildlife?
      │ NO  => REJECT
      ↓ YES
    DUPLICATE CHECK
      │ DUPLICATE => REJECT
      ↓ UNIQUE
    SOURCE VERIFY
      ↓
    DATABASE
      ↓
    PDF GENERATOR
    """

    @staticmethod
    def process_article(
        raw_entry: Any,
        title: str,
        content: str,
        link: str,
        source_name: str,
        is_tamil: bool = False,
        batch_articles: Optional[List[Article]] = None
    ) -> Optional[Article]:
        today_date = datetime.now(IST).date()
        title_clean = title.strip()
        content_clean = content.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip() if content else title_clean

        if not title_clean:
            logger.info("REJECTED: Article missing title.")
            return None

        # ── 1. EXTRACT ORIGINAL PUBLICATION DATE & DATE FILTER ──
        pub_dt = parse_entry_datetime(raw_entry)
        if not pub_dt:
            logger.info(f"REJECTED ('{title_clean}'): Could not extract ORIGINAL publication date/time.")
            return None

        pub_date = pub_dt.date()
        if pub_date != today_date:
            logger.info(f"REJECTED ('{title_clean}'): Date filter failed. Original pub date {pub_date} != today's date {today_date}.")
            return None

        # ── 2. LOCATION FILTER: Tamil Nadu related? ──
        if not ArticleClassifier.is_tamil_nadu_relevant(title_clean, content_clean):
            logger.info(f"REJECTED ('{title_clean}'): Location filter failed. Not related to Tamil Nadu.")
            return None

        # ── 3. TOPIC FILTER: Forest / Wildlife related? ──
        if not ArticleClassifier.is_forest_or_wildlife_relevant(title_clean, content_clean):
            logger.info(f"REJECTED ('{title_clean}'): Topic filter failed. Not related to Forest/Wildlife.")
            return None

        # ── 4. DUPLICATE CHECK ──
        existing_db = list(db_storage.articles.values())
        batch_list = batch_articles or []
        is_duplicate = any(a.source_url == link or a.title_en.lower() == title_clean.lower() or (a.title_ta and a.title_ta.lower() == title_clean.lower()) for a in existing_db + batch_list)
        if is_duplicate:
            logger.info(f"REJECTED ('{title_clean}'): Duplicate check failed. Already exists in DB or batch.")
            return None

        # ── 5. SOURCE VERIFY ──
        clean_source = source_name.strip() if source_name else "Open Source Media"
        if " - " in title_clean and clean_source in ["Google News", "Open Source Media", "Tamil News Outlet", "Bing News Media"]:
            parts = title_clean.rsplit(" - ", 1)
            title_clean = parts[0].strip()
            clean_source = parts[1].strip()

        clean_link = link.strip() if link and link != "#" else "https://news.google.com"

        # ── 6. AI TRANSLATION, CLASSIFICATION, SUMMARIZATION ──
        if is_tamil:
            title_ta = title_clean
            content_ta = content_clean
            title_en, content_en = ArticleTranslator.translate_to_english(title_ta, content_ta)
        else:
            title_en = title_clean
            content_en = content_clean
            title_ta, content_ta = ArticleTranslator.translate_to_tamil(title_en, content_en)

        ai_meta = ArticleClassifier.classify(title_en, content_en, published_at=pub_dt)
        sum_en = ArticleSummarizer.summarize_en(title_en, content_en)
        sum_ta = ArticleSummarizer.summarize_ta(title_ta, content_ta)

        # ── 7. DATABASE SAVE MODEL ──
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
            source_name=clean_source,
            source_url=clean_link,
            published_at=pub_dt,
            tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
            key_entities=ai_meta["key_entities"],
            sentiment=ai_meta["sentiment"],
            date_status="TODAY"
        )

        return art
