from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app.collectors.rss import RSSCollector
from app.collectors.tamil_news import TamilNewsCollector
from app.collectors.english_news import EnglishNewsCollector
from app.pdf.generator import PDFReportGenerator
from app.services.storage import db_storage

scheduler = BackgroundScheduler()

def run_collection_job():
    """
    Automated background job to refresh all wildlife news feeds.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled news collection...")
    rss_count = RSSCollector.fetch_all()
    ta_count = TamilNewsCollector.scrape_latest()
    en_count = EnglishNewsCollector.scrape_latest()
    print(f"Job Finished. Articles fetched -> RSS: {rss_count}, Tamil: {ta_count}, English: {en_count}")

from datetime import datetime, timedelta

def generate_morning_digest_job():
    """
    Auto-generates Morning 8:00 AM Wildlife Alert PDF Digest (Yesterday's + Early Morning News).
    """
    now = datetime.now()
    morning_cutoff = now.replace(hour=8, minute=0, second=0, microsecond=0)
    cutoff_24h_ago = morning_cutoff - timedelta(hours=24)

    all_articles = db_storage.get_articles()
    morning_articles = [
        a for a in all_articles
        if cutoff_24h_ago <= a.published_at <= morning_cutoff
    ]
    if not morning_articles:
        morning_articles = [a for a in all_articles if a.published_at <= morning_cutoff] or all_articles[:15]

    report = PDFReportGenerator.generate_report(
        title=f"Morning Wildlife Alert Bulletin - {now.strftime('%d %b %Y, 08:00 AM')}",
        report_type="Daily Morning Briefing (Yesterday & Early AM Data)",
        articles=morning_articles[:15],
        filter_criteria={"Time Window": "Yesterday 08:00 AM to Today 08:00 AM"}
    )
    print(f"Generated automated 08:00 AM morning PDF report: {report.download_url}")

def generate_evening_digest_job():
    """
    Auto-generates Evening 5:30 PM Wildlife Alert PDF Digest (8:00 AM to 5:00 PM Daytime News).
    """
    now = datetime.now()
    start_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_5pm = now.replace(hour=17, minute=0, second=0, microsecond=0)

    all_articles = db_storage.get_articles()
    daytime_articles = [
        a for a in all_articles
        if start_8am <= a.published_at <= end_5pm
    ]
    if not daytime_articles:
        daytime_articles = [a for a in all_articles if a.published_at >= start_8am] or all_articles[:15]

    report = PDFReportGenerator.generate_report(
        title=f"Evening Wildlife Summary Briefing - {now.strftime('%d %b %Y, 05:30 PM')}",
        report_type="Daily Evening Briefing (08:00 AM - 05:00 PM Data)",
        articles=daytime_articles[:15],
        filter_criteria={"Time Window": "Today 08:00 AM to 05:00 PM"}
    )
    print(f"Generated automated 05:30 PM evening PDF report: {report.download_url}")

def start_scheduler():
    if not scheduler.running:
        # Schedule news fetch every 15 minutes
        scheduler.add_job(run_collection_job, 'interval', minutes=15, id='news_fetch_job')
        # Schedule morning PDF strictly at 08:00 AM
        scheduler.add_job(generate_morning_digest_job, 'cron', hour=8, minute=0, id='morning_digest_job')
        # Schedule evening PDF strictly at 05:30 PM (17:30)
        scheduler.add_job(generate_evening_digest_job, 'cron', hour=17, minute=30, id='evening_digest_job')
        
        scheduler.start()
        print("APScheduler active: Auto-generating PDF digests EXCLUSIVELY at 08:00 AM and 05:30 PM.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
