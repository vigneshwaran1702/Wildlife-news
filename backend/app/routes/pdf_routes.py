import os
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.models.schemas import PDFReport
from app.pdf.generator import PDFReportGenerator
from app.services.storage import db_storage

router = APIRouter(prefix="/api/pdf", tags=["PDF Reports"])

class PDFGenerateRequest(BaseModel):
    title: str
    report_type: str = "Custom Briefing"
    category: Optional[str] = None
    district: Optional[str] = None
    conflict_level: Optional[str] = None

from app.scheduler.jobs import scheduler

def generate_shift_pdf_by_id(shift_id: int) -> PDFReport:
    now = datetime.now()
    all_articles = db_storage.get_articles()

    if shift_id == 1:
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=17, minute=0, second=0, microsecond=0)
        articles = [a for a in all_articles if start_time <= a.published_at <= end_time]
        if not articles:
            articles = [a for a in all_articles if a.published_at >= start_time] or all_articles[:15]

        title = f"Shift 1 Day Bulletin (8:00 AM - 5:00 PM) - {now.strftime('%d %b %Y')}"
        report_type = "Shift 1: Day Bulletin (08:00 AM - 05:00 PM)"
        filter_criteria = {
            "Time Window": "Today 08:00 AM to 05:00 PM",
            "Auto Schedule": "17:00 (5:00 PM) Daily Trigger",
            "Endpoint": "/api/pdf/trigger-shift/1"
        }
    elif shift_id == 2:
        start_time = now.replace(hour=17, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        articles = [a for a in all_articles if start_time <= a.published_at <= end_time]
        if not articles:
            articles = [a for a in all_articles if a.published_at >= start_time] or all_articles[:15]

        title = f"Shift 2 Evening Bulletin (5:00 PM - 9:00 PM) - {now.strftime('%d %b %Y')}"
        report_type = "Shift 2: Evening Bulletin (05:00 PM - 09:00 PM)"
        filter_criteria = {
            "Time Window": "Today 05:00 PM to 09:00 PM",
            "Deduplication": "Excludes Shift 1 (8am-5pm) News",
            "Auto Schedule": "21:00 (9:00 PM) Daily Trigger",
            "Endpoint": "/api/pdf/trigger-shift/2"
        }
    elif shift_id == 3:
        end_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        start_time = (end_time - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        articles = [a for a in all_articles if start_time <= a.published_at <= end_time]
        if not articles:
            articles = [a for a in all_articles if a.published_at <= end_time] or all_articles[:15]

        title = f"Shift 3 Night & Early Morning Bulletin (9:00 PM - 8:00 AM) - {now.strftime('%d %b %Y')}"
        report_type = "Shift 3: Night & Early Morning Bulletin (09:00 PM - 08:00 AM)"
        filter_criteria = {
            "Time Window": "Yesterday 09:00 PM to Today 08:00 AM",
            "Deduplication": "Excludes Daytime & Evening News",
            "Auto Schedule": "08:00 (8:00 AM) Daily Trigger",
            "Endpoint": "/api/pdf/trigger-shift/3"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid shift ID. Choose 1 (Day: 8am-5pm), 2 (Evening: 5pm-9pm), or 3 (Night: yesterday 9pm-8am).")

    return PDFReportGenerator.generate_report(
        title=title,
        report_type=report_type,
        articles=articles,
        filter_criteria=filter_criteria
    )

@router.get("/schedule")
def get_pdf_schedule():
    jobs = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            if "digest" in job.id:
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "Scheduled"
                jobs.append({
                    "job_id": job.id,
                    "next_run_time": next_run
                })
    return {
        "status": "Active",
        "shift3_timeline": "08:00 IST -> Night Digest (yesterday 9pm-8am)",
        "shift3_trigger_url": "/api/pdf/trigger-shift/3",
        "shift1_timeline": "17:00 IST -> Day Digest (8am-5pm)",
        "shift1_trigger_url": "/api/pdf/trigger-shift/1",
        "shift2_timeline": "21:00 IST -> Evening Digest (5pm-9pm)",
        "shift2_trigger_url": "/api/pdf/trigger-shift/2",
        "scheduled_jobs": jobs
    }

@router.get("/trigger-shift/{shift_id}")
@router.post("/trigger-shift/{shift_id}")
def trigger_shift_pdf(shift_id: int, as_json: bool = False):
    report = generate_shift_pdf_by_id(shift_id)

    if as_json:
        return report

    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=500, detail="Generated PDF file not found")

    filename = os.path.basename(report.file_path)
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/reports", response_model=List[PDFReport])
def list_pdf_reports():
    return db_storage.get_reports()

@router.post("/generate", response_model=PDFReport)
def generate_pdf_report(payload: PDFGenerateRequest):
    articles = db_storage.get_articles(
        category=payload.category,
        district=payload.district,
        conflict_level=payload.conflict_level
    )

    now = datetime.now()
    filter_dict = {
        "Category": payload.category or "All",
        "District": payload.district or "All",
        "Risk Level": payload.conflict_level or "All"
    }

    # Time Window filtering for 3 distinct shifts
    if "Shift 1" in payload.report_type or "8am-5pm" in payload.report_type or "Day" in payload.report_type:
        return generate_shift_pdf_by_id(1)
    elif "Shift 2" in payload.report_type or "5pm-9pm" in payload.report_type or "Evening" in payload.report_type:
        return generate_shift_pdf_by_id(2)
    elif "Shift 3" in payload.report_type or "9pm-8am" in payload.report_type or "Night" in payload.report_type:
        return generate_shift_pdf_by_id(3)

    if not articles:
        articles = db_storage.get_articles()[:10]  # Fallback to top 10

    report = PDFReportGenerator.generate_report(
        title=payload.title,
        report_type=payload.report_type,
        articles=articles,
        filter_criteria=filter_dict
    )

    return report

@router.get("/download/{report_id}")
def download_pdf(report_id: str):
    report = db_storage.reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(report.file_path, media_type="application/pdf", filename=os.path.basename(report.file_path))

