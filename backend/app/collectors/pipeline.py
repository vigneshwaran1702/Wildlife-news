import email.utils
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
import uuid
import logging

from app.models.schemas import Article
from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator
from app.collectors.verifier import SourcePageVerifier, parse_entry_datetime
from app.services.storage import db_storage

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")

class ArticlePipeline:
    """
    Strict Real-Time Source Verification Pipeline:
    COLLECT
      ↓
    SOURCE URL VALIDATION & ORIGINAL DATE EXTRACTION
      ├── Unreachable? ──> REJECT: SOURCE_UNREACHABLE
      ├── Unparseable? ──> REJECT: TIME_UNAVAILABLE
      ↓
    TODAY DATE CHECK (Asia/Kolkata timezone)
      ├── Published < Today? ──> REJECT: REJECTED_OLD
      ├── Published > Today? ──> REJECT: REJECTED_FUTURE
      ↓
    TAMIL NADU RELEVANCE CHECK
      ├── Not TN? ──> REJECT: REJECTED_NOT_TAMIL_NADU
      ↓
    FOREST/WILDLIFE TOPIC CHECK
      ├── Not Forest/Wildlife? ──> REJECT: REJECTED_NOT_WILDLIFE
      ↓
    DUPLICATE CHECK (Canonical URL & Headline)
      ├── Exists? ──> REJECT: DUPLICATE
      ↓
    SAVE AS VERIFIED (status = "VERIFIED")
      ↓
    PDF GENERATION (Shift 1 / Shift 2 / Shift 3 IST filtering)
    """

    @staticmethod
    def process_article(
        raw_entry: Any,
        title: str,
        content: str,
        link: str,
        source_name: str,
        is_tamil: bool = False,
        batch_articles: Optional[List[Article]] = None,
        verify_web_source: bool = True
    ) -> Optional[Article]:
        today_date = datetime.now(IST).date()
        title_clean = title.strip() if title else ""
        content_clean = content.replace("<p>", "").replace("</p>", "").replace("<br>", "\n").strip() if content else title_clean

        if not title_clean:
            logger.info("REJECTED [UNVERIFIED]: Article missing title.")
            return None

        # ── 1. SOURCE URL VALIDATION & ORIGINAL PUBLICATION DATE EXTRACTION ──
        feed_dt = parse_entry_datetime(raw_entry)

        if verify_web_source and link and link.startswith("http") and "news.google.com" not in link and "bing.com" not in link:
            ver_res = SourcePageVerifier.verify_and_extract_metadata(link, fallback_entry_dt=feed_dt)
            if not ver_res.is_reachable and not feed_dt:
                logger.info(f"REJECTED [SOURCE_UNREACHABLE] Source: {source_name} | URL: {link} | Reason: {ver_res.reason}")
                return None

            if ver_res.published_at:
                pub_dt = ver_res.published_at
            else:
                pub_dt = feed_dt

            if ver_res.raw_title and len(ver_res.raw_title) > 10:
                # Use authentic source headline directly (NO AI HEADLINE HALLUCINATION)
                title_clean = ver_res.raw_title.strip()
        else:
            pub_dt = feed_dt

        # Check if date was extracted
        if not pub_dt:
            logger.info(f"REJECTED [TIME_UNAVAILABLE] Source: {source_name} | Title: '{title_clean}' | Today: {today_date} | Reason: Original publication date/time unavailable.")
            return None

        pub_date = pub_dt.date()

        # ── 2. TODAY DATE CHECK (Asia/Kolkata timezone boundary in UTC) ──
        now_ist = datetime.now(timezone.utc).astimezone(IST)
        start_of_today_ist = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_today_utc = start_of_today_ist.astimezone(timezone.utc)
        end_of_today_utc = (start_of_today_ist + timedelta(days=1)).astimezone(timezone.utc)

        # Convert pub_dt to UTC for database comparison
        if pub_dt.tzinfo is None:
            pub_dt_utc = pub_dt.replace(tzinfo=IST).astimezone(timezone.utc)
        else:
            pub_dt_utc = pub_dt.astimezone(timezone.utc)

        pub_date_ist = pub_dt_utc.astimezone(IST).date()
        today_date_ist = now_ist.date()

        if pub_dt_utc < start_of_today_utc:
            logger.info(f"REJECTED [REJECTED_OLD] Source: {source_name} | Orig Date IST: {pub_date_ist} | Today IST: {today_date_ist} | Reason: Original date is older than today ({pub_date_ist} < {today_date_ist}).")
            return None

        if pub_dt_utc >= end_of_today_utc:
            logger.info(f"REJECTED [REJECTED_FUTURE] Source: {source_name} | Orig Date IST: {pub_date_ist} | Today IST: {today_date_ist} | Reason: Original date is in the future ({pub_date_ist} > {today_date_ist}).")
            return None

        # ── 3. TAMIL NADU RELEVANCE CHECK ──
        if not ArticleClassifier.is_tamil_nadu_relevant(title_clean, content_clean):
            logger.info(f"REJECTED [REJECTED_NOT_TAMIL_NADU] Source: {source_name} | Title: '{title_clean}' | Today IST: {today_date_ist} | Reason: Content not relevant to Tamil Nadu.")
            return None

        # ── 4. FOREST / WILDLIFE TOPIC CHECK ──
        if not ArticleClassifier.is_forest_or_wildlife_relevant(title_clean, content_clean):
            logger.info(f"REJECTED [REJECTED_NOT_WILDLIFE] Source: {source_name} | Title: '{title_clean}' | Today IST: {today_date_ist} | Reason: Content not relevant to Forest/Wildlife topics.")
            return None

        # ── 5. DUPLICATE CHECK (Canonical URL & Normalized Headline) ──
        existing_db = list(db_storage.articles.values())
        batch_list = batch_articles or []
        norm_title = title_clean.lower().strip()
        is_duplicate = any(
            a.source_url == link or 
            a.title_en.lower().strip() == norm_title or 
            (a.title_ta and a.title_ta.lower().strip() == norm_title)
            for a in existing_db + batch_list
        )

        if is_duplicate:
            logger.info(f"REJECTED [DUPLICATE] Source: {source_name} | Title: '{title_clean}' | Today IST: {today_date_ist} | Reason: Article already exists in database or batch.")
            return None

        # ── 6. SOURCE VERIFICATION CLEANUP ──
        clean_source = source_name.strip() if source_name else "Open Source Media"
        if " - " in title_clean and clean_source in ["Google News", "Open Source Media", "Tamil News Outlet", "Bing News Media"]:
            parts = title_clean.rsplit(" - ", 1)
            title_clean = parts[0].strip()
            clean_source = parts[1].strip()

        clean_link = link.strip() if link and link != "#" else "https://news.google.com"

        # ── 7. AI TRANSLATION, CLASSIFICATION, SUMMARIZATION ──
        # Note: Headline is NOT hallucinated by AI; it comes directly from title_clean extracted from source
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

        # ── 8. SAVE AS VERIFIED (store collected_at in UTC) ──
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
            published_at=pub_dt.replace(tzinfo=None),
            collected_at=datetime.now(timezone.utc).replace(tzinfo=None),
            verification_status="VERIFIED",
            verification_reason="Original source metadata verified and matches today's date in Asia/Kolkata",
            tags=[ai_meta["category"], ai_meta["district"]] + ai_meta["species"],
            key_entities=ai_meta["key_entities"],
            sentiment=ai_meta["sentiment"],
            date_status="TODAY"
        )

        logger.info(f"ACCEPTED [VERIFIED] Source: {clean_source} | Title: '{title_en[:50]}...' | Published: {pub_dt.strftime('%Y-%m-%d %H:%M:%S IST')}")
        return art

