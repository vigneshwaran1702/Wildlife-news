import sys
import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.collectors.pipeline import ArticlePipeline
from app.services.storage import db_storage
from app.routes.pdf_routes import generate_shift_pdf_by_id

IST = ZoneInfo("Asia/Kolkata")
now = datetime.now(IST)
today = now.date()
yesterday = today - timedelta(days=1)
two_days_ago = today - timedelta(days=2)
tomorrow = today + timedelta(days=1)

print("==================================================")
print("RUNNING COMPREHENSIVE PIPELINE & PDF SHIFT TEST SUITE")
print(f"Current Date/Time (Asia/Kolkata): {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
print("==================================================")

# Clear storage for clean test environment
db_storage.articles.clear()

# ── TEST CASE 1: Article published TODAY -> Must be ACCEPTED (VERIFIED) ──
raw_today = {"published": datetime.combine(today, time(9, 30, 0)).strftime("%Y-%m-%d %H:%M:%S")}
art_today = ArticlePipeline.process_article(
    raw_entry=raw_today,
    title="Coimbatore Forest Division installs 10 AI thermal sensors along railway elephant corridor",
    content="Coimbatore Forest Division installed AI thermal sensor warning sirens along Mettupalayam rail line to alert train pilots when wild elephant herds cross.",
    link="https://www.thehindu.com/news/national/tamil-nadu/coimbatore-ai-railway-elephant-corridor-today",
    source_name="The Hindu",
    verify_web_source=False
)
print(f"[TEST 1] Published TODAY article: Status = {art_today.verification_status if art_today else None}")
assert art_today is not None and art_today.verification_status == "VERIFIED", "TEST 1 FAILED: Article published today was rejected!"

# ── TEST CASE 2: Article published > 36 Hours Ago -> Must be REJECTED (REJECTED_OLD) ──
raw_yesterday = {"published": (now - timedelta(hours=50)).strftime("%Y-%m-%d %H:%M:%S")}
art_yesterday = ArticlePipeline.process_article(
    raw_entry=raw_yesterday,
    title="Yesterday News: Sathyamangalam Tiger Reserve sets up 24x7 control room",
    content="Sathyamangalam Tiger Reserve authorities set up a control room yesterday.",
    link="https://www.newindianexpress.com/states/tamil-nadu/str-yesterday-news",
    source_name="The New Indian Express",
    verify_web_source=False
)
print(f"[TEST 2] Published YESTERDAY article: Status = {art_yesterday}")
assert art_yesterday is None, "TEST 2 FAILED: Article published yesterday was accepted!"

# ── TEST CASE 3: Article published TWO DAYS AGO -> Must be REJECTED (REJECTED_OLD) ──
raw_2days = {"published": datetime.combine(two_days_ago, time(11, 0, 0)).strftime("%Y-%m-%d %H:%M:%S")}
art_2days = ArticlePipeline.process_article(
    raw_entry=raw_2days,
    title="Two Days Ago News: Mudumalai tiger census completed",
    content="Forest officials completed tiger census two days ago in Mudumalai.",
    link="https://www.dtnext.in/mudumalai-census-2days-ago",
    source_name="DT Next",
    verify_web_source=False
)
print(f"[TEST 3] Published TWO DAYS AGO article: Status = {art_2days}")
assert art_2days is None, "TEST 3 FAILED: Article published 2 days ago was accepted!"

# ── TEST CASE 4: FUTURE-DATED Article -> Must be REJECTED (REJECTED_FUTURE) ──
raw_future = {"published": datetime.combine(tomorrow, time(10, 0, 0)).strftime("%Y-%m-%d %H:%M:%S")}
art_future = ArticlePipeline.process_article(
    raw_entry=raw_future,
    title="Future News: Tamil Nadu Forest Policy 2027 draft release",
    content="Tamil Nadu Forest Department will publish policy document tomorrow.",
    link="https://www.dailythanthi.com/future-policy-2027",
    source_name="Dina Thanthi",
    verify_web_source=False
)
print(f"[TEST 4] FUTURE-DATED article: Status = {art_future}")
assert art_future is None, "TEST 4 FAILED: Future-dated article was accepted!"

# ── TEST CASE 5: Article with NO RELIABLE PUBLICATION DATE -> Must be REJECTED (TIME_UNAVAILABLE) ──
raw_nodate = {}
art_nodate = ArticlePipeline.process_article(
    raw_entry=raw_nodate,
    title="Undated News: Anamalai Tiger Reserve bamboo rafting eco-tourism opened",
    content="Anamalai Tiger Reserve opened eco-tourism bamboo rafting in Topslip.",
    link="https://www.dtnext.in/anamalai-rafting-undated",
    source_name="DT Next",
    verify_web_source=False
)
print(f"[TEST 5] UNDATED article: Status = {art_nodate}")
assert art_nodate is None, "TEST 5 FAILED: Undated article was accepted into time-based collection!"

# ── TEST CASE 6: Article collected TODAY but published 48 HOURS AGO -> Must be REJECTED (REJECTED_OLD) ──
raw_collected_today_pub_yesterday = {
    "published": (now - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S"),
    "collected_at": now.strftime("%Y-%m-%d %H:%M:%S")
}
art_collected_today_old = ArticlePipeline.process_article(
    raw_entry=raw_collected_today_pub_yesterday,
    title="Collected Today But Published Yesterday: Megamalai corridor eviction order",
    content="Madras High Court ordered eviction of resort encroachments yesterday night.",
    link="https://www.thehindu.com/megamalai-eviction-collected-today",
    source_name="The Hindu",
    verify_web_source=False
)
print(f"[TEST 6] Collected TODAY but published YESTERDAY article: Status = {art_collected_today_old}")
assert art_collected_today_old is None, "TEST 6 FAILED: Article collected today but published yesterday was accepted!"

# ── TEST CASE 7: Genuine Article published TODAY within Shift 1 Window -> Included in Shift 1 PDF ──
db_storage.add_article(art_today)
pdf_report = generate_shift_pdf_by_id(1)
print(f"[TEST 7] Shift 1 PDF Report Generation: PDF ID = {pdf_report.id}, Article Count = {pdf_report.article_count}")
assert pdf_report.article_count == 1, f"TEST 7 FAILED: Expected 1 article in Shift 1 PDF, found {pdf_report.article_count}"

print("\n==================================================")
print("ALL 7 TEST CASES PASSED SUCCESSFULLY!")
print("==================================================")
