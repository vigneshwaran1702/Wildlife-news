"""
Shared helpers for the news collectors.
"""

from bs4 import BeautifulSoup


def clean_html(raw: str) -> str:
    """
    Strip HTML tags from RSS/API description text and collapse whitespace.

    Google News RSS descriptions arrive wrapped in markup like:
        <a href="...">Headline</a>&nbsp;&nbsp;<font color="#6f6f6f">Source</font>
    This extracts the readable text only, so it's safe to store and display
    as plain text (e.g. in content_en/content_ta) without leaking raw tags.
    """
    if not raw:
        return ""
    text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
    return " ".join(text.split())
