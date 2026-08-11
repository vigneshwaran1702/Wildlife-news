"""
One-off cleanup for articles collected before the HTML-stripping fix.

Strips leaked <a>/<font> markup out of content_en/content_ta, then
regenerates summary_en/summary_ta from the cleaned content so the
Key Highlights bullets read correctly too (the old bullets were built
from the raw HTML blob).

Run this once against the live backend's data directory:
    cd backend
    python ../scripts/retro_clean_html.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage
from app.collectors.html_utils import clean_html
from app.ai.summarizer import ArticleSummarizer

fixed = 0

for art in db_storage.articles.values():
    before_en = art.content_en
    before_ta = art.content_ta

    art.content_en = clean_html(art.content_en)
    art.content_ta = clean_html(art.content_ta)

    if art.content_en != before_en or art.content_ta != before_ta:
        art.summary_en = ArticleSummarizer.summarize_en(art.title_en, art.content_en)
        art.summary_ta = ArticleSummarizer.summarize_ta(art.title_ta, art.content_ta)
        fixed += 1

db_storage.save_data()
print(f"Cleaned {fixed} of {len(db_storage.articles)} articles (re-summarized where content changed).")
