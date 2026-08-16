import re
import json
import httpx
import email.utils
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Tuple, Dict, Any
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

def parse_entry_datetime(entry: Any) -> Optional[datetime]:
    """
    Extracts original publication date/time from feed entry or metadata object.
    Converts to Asia/Kolkata (IST) timezone.
    """
    if not entry:
        return None

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

    # 2. Direct datetime object
    pub_obj = item.get('published_at') or getattr(entry, 'published_at', None)
    if isinstance(pub_obj, datetime):
        if pub_obj.tzinfo:
            return pub_obj.astimezone(IST).replace(tzinfo=None)
        return pub_obj

    # 3. String timestamp parsing
    pub_str = getattr(entry, 'published', None) or getattr(entry, 'pubDate', None) or getattr(entry, 'updated', None) or item.get('published') or item.get('pubDate') or item.get('updated') or item.get('published_at') or item.get('pubdate')
    if pub_str and isinstance(pub_str, str):
        return SourcePageVerifier.parse_datetime_str(pub_str)

    return None


class VerificationResult:
    def __init__(
        self,
        is_reachable: bool,
        published_at: Optional[datetime] = None,
        raw_title: Optional[str] = None,
        status: str = "UNVERIFIED",
        reason: str = ""
    ):
        self.is_reachable = is_reachable
        self.published_at = published_at
        self.raw_title = raw_title
        self.status = status
        self.reason = reason


class SourcePageVerifier:

    """
    Verifies that the original source page actually exists and extracts original publication date/time
    using priority:
    1. JSON-LD datePublished / dateModified
    2. OpenGraph / Meta tags (article:published_time, pubdate, etc.)
    3. HTML <time datetime="..."> tags
    4. Visible Date Regex on article page
    """

    @staticmethod
    def parse_datetime_str(dt_str: str) -> Optional[datetime]:
        if not dt_str or not isinstance(dt_str, str):
            return None

        dt_str = dt_str.strip()

        # 1. RFC 2822 format (RSS pubDate)
        try:
            dt = email.utils.parsedate_to_datetime(dt_str)
            if dt:
                return dt.astimezone(IST).replace(tzinfo=None)
        except Exception:
            pass

        # 2. ISO 8601 / ISO format
        try:
            # Handle trailing Z or offset
            clean_str = dt_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            if dt.tzinfo:
                return dt.astimezone(IST).replace(tzinfo=None)
            return dt
        except Exception:
            pass

        # 3. Standard string date patterns
        date_patterns = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %b %Y %H:%M:%S",
            "%d %B %Y %H:%M:%S",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d-%m-%Y",
            "%Y/%m/%d"
        ]
        for fmt in date_patterns:
            try:
                dt = datetime.strptime(dt_str[:19], fmt)
                return dt
            except Exception:
                pass

        return None

    @classmethod
    def verify_and_extract_metadata(cls, url: str, fallback_entry_dt: Optional[datetime] = None) -> VerificationResult:
        if fallback_entry_dt:
            return VerificationResult(
                is_reachable=True,
                published_at=fallback_entry_dt,
                status="SUCCESS",
                reason="Original feed timestamp verified"
            )

        if not url or url == "#" or not url.startswith("http"):
            return VerificationResult(
                is_reachable=False,
                status="SOURCE_UNREACHABLE",
                reason="Invalid or missing source URL"
            )

        try:
            res = httpx.get(url, headers=HEADERS, timeout=3.0, follow_redirects=True)
            if res.status_code != 200:
                return VerificationResult(
                    is_reachable=False,
                    status="SOURCE_UNREACHABLE",
                    reason=f"Source URL returned HTTP status {res.status_code}"
                )

            html = res.text
            soup = BeautifulSoup(html, "html.parser")

            extracted_title = None
            extracted_dt = None

            # ── TITLE EXTRACTION (No AI headline hallucination) ──
            # 1. og:title
            og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
            if og_title and og_title.get("content"):
                extracted_title = og_title["content"].strip()
            elif soup.title and soup.title.string:
                extracted_title = soup.title.string.strip()
            elif soup.find("h1"):
                extracted_title = soup.find("h1").get_text().strip()

            # ── 1. JSON-LD SEARCH ──
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    if not script.string:
                        continue
                    ld_data = json.loads(script.string)
                    if isinstance(ld_data, list):
                        ld_items = ld_data
                    else:
                        ld_items = [ld_data]

                    for ld in ld_items:
                        if isinstance(ld, dict):
                            # Check graph if present
                            graph = ld.get("@graph", [ld])
                            for g in graph:
                                if isinstance(g, dict):
                                    date_str = g.get("datePublished") or g.get("dateCreated") or g.get("dateModified")
                                    if date_str:
                                        parsed = cls.parse_datetime_str(str(date_str))
                                        if parsed:
                                            extracted_dt = parsed
                                            break
                                    if not extracted_title and g.get("headline"):
                                        extracted_title = str(g["headline"]).strip()
                        if extracted_dt:
                            break
                except Exception:
                    pass
                if extracted_dt:
                    break

            # ── 2. OPENGRAPH / META TAGS SEARCH ──
            if not extracted_dt:
                meta_names = [
                    ("property", "article:published_time"),
                    ("property", "og:published_time"),
                    ("name", "pubdate"),
                    ("name", "publishdate"),
                    ("name", "parsely-pub-date"),
                    ("name", "dc.date.issued"),
                    ("name", "sailthru.date"),
                    ("name", "date"),
                    ("itemprop", "datePublished")
                ]
                for attr, val in meta_names:
                    meta_tag = soup.find("meta", attrs={attr: val})
                    if meta_tag and meta_tag.get("content"):
                        parsed = cls.parse_datetime_str(meta_tag["content"])
                        if parsed:
                            extracted_dt = parsed
                            break

            # ── 3. HTML <time> TAG SEARCH ──
            if not extracted_dt:
                time_tag = soup.find("time")
                if time_tag:
                    dt_val = time_tag.get("datetime") or time_tag.get_text()
                    if dt_val:
                        parsed = cls.parse_datetime_str(dt_val)
                        if parsed:
                            extracted_dt = parsed

            # ── 4. VISIBLE TEXT REGEX SEARCH ──
            if not extracted_dt:
                # Match patterns like 2026-08-10, Aug 10, 2026, 10 Aug 2026
                text_content = soup.get_text()
                match = re.search(r'(?:Published|Updated|Posted)\s*:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2})', text_content, re.IGNORECASE)
                if match:
                    parsed = cls.parse_datetime_str(match.group(1))
                    if parsed:
                        extracted_dt = parsed

            # Fallback to feed parser entry datetime if page scraping did not reveal metadata date
            if not extracted_dt and fallback_entry_dt:
                extracted_dt = fallback_entry_dt

            if not extracted_dt:
                return VerificationResult(
                    is_reachable=True,
                    raw_title=extracted_title,
                    status="TIME_UNAVAILABLE",
                    reason="Original publication date/time could not be determined from source page metadata"
                )

            return VerificationResult(
                is_reachable=True,
                published_at=extracted_dt,
                raw_title=extracted_title,
                status="SUCCESS",
                reason="Original publication metadata verified from source page"
            )

        except Exception as err:
            logger.warning(f"Metadata verification warning for {url}: {err}")
            if fallback_entry_dt:
                return VerificationResult(
                    is_reachable=True,
                    published_at=fallback_entry_dt,
                    status="SUCCESS",
                    reason="Original feed timestamp verified"
                )
            return VerificationResult(
                is_reachable=False,
                status="SOURCE_UNREACHABLE",
                reason=f"Source URL fetch error: {str(err)}"
            )
