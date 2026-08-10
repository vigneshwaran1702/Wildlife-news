from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.collectors.rss import RSSCollector
from app.collectors.tamil_news import TamilNewsCollector
from app.collectors.english_news import EnglishNewsCollector
from app.collectors.bing_collector import BingNewsCollector
from app.pdf.generator import PDFReportGenerator
from app.services.storage import db_storage

IST = ZoneInfo("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)

def run_collection_job():
    """
    Automated background job to refresh all wildlife news feeds.
    """
    now_ist = datetime.now(IST)
    print(f"[{now_ist.strftime('%Y-%m-%d %H:%M:%S IST')}] Starting scheduled news collection...")
    rss_count = RSSCollector.fetch_all()
    ta_count = TamilNewsCollector.scrape_latest()
    en_count = EnglishNewsCollector.scrape_latest()
    bing_count = BingNewsCollector.scrape_latest()
    print(f"Job Finished. Articles fetched -> RSS: {rss_count}, Tamil: {ta_count}, English: {en_count}, Bing: {bing_count}")

def generate_shift1_day_digest_job():
    """
    Auto-generates Shift 1 PDF Digest (Today 8:00 AM to 5:00 PM Daytime News) at 5:00 PM (17:00 IST).
    """
    from app.routes.pdf_routes import generate_shift_pdf_by_id
    report = generate_shift_pdf_by_id(1)
    print(f"[{datetime.now(IST).strftime('%I:%M %p IST')}] Generated automated Shift 1 (08:00 AM - 05:00 PM) PDF report: {report.download_url}")

def generate_shift2_evening_digest_job():
    """
    Auto-generates Shift 2 PDF Digest (Today 5:00 PM to 9:00 PM Evening News) at 9:00 PM (21:00 IST).
    """
    from app.routes.pdf_routes import generate_shift_pdf_by_id
    report = generate_shift_pdf_by_id(2)
    print(f"[{datetime.now(IST).strftime('%I:%M %p IST')}] Generated automated Shift 2 (05:00 PM - 09:00 PM) PDF report: {report.download_url}")

def generate_shift3_night_digest_job():
    """
    Auto-generates Shift 3 PDF Digest (Yesterday 9:00 PM to Today 8:00 AM Overnight News) at 8:00 AM (08:00 IST).
    """
    from app.routes.pdf_routes import generate_shift_pdf_by_id
    report = generate_shift_pdf_by_id(3)
    print(f"[{datetime.now(IST).strftime('%I:%M %p IST')}] Generated automated Shift 3 (09:00 PM - 08:00 AM) PDF report: {report.download_url}")

def check_and_generate_due_pdfs():
    """
    Guarantees PDF reports generate even if the server was started after the exact cron time in IST.
    """
    now = datetime.now(IST)
    today_str = now.strftime('%Y-%m-%d')
    existing_reports = db_storage.get_reports()
    existing_types = [
        r.report_type for r in existing_reports
        if r.created_at and r.created_at.strftime('%Y-%m-%d') == today_str
    ]

    # Shift 3 Night (8:00 AM IST): Due if current IST time is past 8:00 AM and report not yet created today
    if now.hour >= 8 and "Shift 3: Night & Early Morning Bulletin (09:00 PM - 08:00 AM)" not in existing_types:
        print("[Scheduler Startup Catch-Up] Generating Shift 3 Night PDF (due at 8:00 AM IST)...")
        generate_shift3_night_digest_job()

    # Shift 1 Day (5:00 PM / 17:00 IST): Due if current IST time is past 5:00 PM and report not yet created today
    if now.hour >= 17 and "Shift 1: Day Bulletin (08:00 AM - 05:00 PM)" not in existing_types:
        print("[Scheduler Startup Catch-Up] Generating Shift 1 Day PDF (due at 5:00 PM IST)...")
        generate_shift1_day_digest_job()

    # Shift 2 Evening (9:00 PM / 21:00 IST): Due if current IST time is past 9:00 PM and report not yet created today
    if now.hour >= 21 and "Shift 2: Evening Bulletin (05:00 PM - 09:00 PM)" not in existing_types:
        print("[Scheduler Startup Catch-Up] Generating Shift 2 Evening PDF (due at 9:00 PM IST)...")
        generate_shift2_evening_digest_job()

def start_scheduler():
    if not scheduler.running:
        # Continuous Scheduled Collector: Every 3 hours
        scheduler.add_job(run_collection_job, 'interval', hours=3, id='news_fetch_job', misfire_grace_time=3600)

        # ── SHIFT 1: 08:00 AM ➔ 05:00 PM (17:00 IST) ──
        # 8:00 AM IST: Start collecting Morning Shift news
        scheduler.add_job(run_collection_job, 'cron', hour=8, minute=0, id='start_shift1_collect_job', misfire_grace_time=3600)
        # 5:00 PM IST (17:00): Generate Morning Shift PDF (Covers 8:00 AM - 5:00 PM)
        scheduler.add_job(generate_shift1_day_digest_job, 'cron', hour=17, minute=0, id='shift1_digest_job', misfire_grace_time=3600)

        # ── SHIFT 2: 05:00 PM ➔ 09:00 PM (21:00 IST) ──
        # 5:00 PM IST (17:00): Start collecting Evening Shift news
        scheduler.add_job(run_collection_job, 'cron', hour=17, minute=0, id='start_shift2_collect_job', misfire_grace_time=3600)
        # 9:00 PM IST (21:00): Generate Evening Shift PDF (Covers 5:00 PM - 9:00 PM)
        scheduler.add_job(generate_shift2_evening_digest_job, 'cron', hour=21, minute=0, id='shift2_digest_job', misfire_grace_time=3600)

        # ── SHIFT 3: 09:00 PM ➔ 08:00 AM (08:00 IST Next Day) ──
        # 9:00 PM IST (21:00): Start collecting Night Shift news
        scheduler.add_job(run_collection_job, 'cron', hour=21, minute=0, id='start_shift3_collect_job', misfire_grace_time=3600)
        # 8:00 AM IST (08:00 Next Day): Generate Night Shift PDF (Covers 9:00 PM - 8:00 AM)
        scheduler.add_job(generate_shift3_night_digest_job, 'cron', hour=8, minute=0, id='shift3_digest_job', misfire_grace_time=3600)
        
        scheduler.start()
        print("APScheduler active (Asia/Kolkata IST): 3 Shifts (08:00 AM, 17:00 PM, 21:00 PM IST) collection & PDF generation scheduled.")

        # Run instant catch-up check on server launch
        try:
            check_and_generate_due_pdfs()
        except Exception as e:
            print(f"Catch-up check warning: {e}")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

