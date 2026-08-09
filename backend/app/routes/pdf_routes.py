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
        "shift1_timeline": "17:00 (5:00 PM) Daily Trigger (Daytime News: 08:00 AM ➔ 05:00 PM)",
        "shift2_timeline": "21:00 (9:00 PM) Daily Trigger (Evening News: 05:00 PM ➔ 09:00 PM)",
        "shift3_timeline": "08:00 (8:00 AM) Daily Trigger (Night News: 09:00 PM ➔ 08:00 AM)",
        "scheduled_jobs": jobs
    }

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
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=17, minute=0, second=0, microsecond=0)
        time_filtered = [a for a in articles if start_time <= a.published_at <= end_time]
        if not time_filtered:
            time_filtered = [a for a in articles if a.published_at >= start_time]
        if time_filtered:
            articles = time_filtered
        filter_dict["Time Window"] = "Shift 1: Today 08:00 AM to 05:00 PM"

    elif "Shift 2" in payload.report_type or "5pm-9pm" in payload.report_type or "Evening" in payload.report_type:
        start_time = now.replace(hour=17, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        time_filtered = [a for a in articles if start_time <= a.published_at <= end_time]
        if not time_filtered:
            time_filtered = [a for a in articles if a.published_at >= start_time]
        if time_filtered:
            articles = time_filtered
        filter_dict["Time Window"] = "Shift 2: Today 05:00 PM to 09:00 PM (No Duplicate Shift 1 News)"

    elif "Shift 3" in payload.report_type or "9pm-8am" in payload.report_type or "Night" in payload.report_type:
        end_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        start_time = (end_time - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        time_filtered = [a for a in articles if start_time <= a.published_at <= end_time]
        if not time_filtered:
            time_filtered = [a for a in articles if a.published_at <= end_time]
        if time_filtered:
            articles = time_filtered
        filter_dict["Time Window"] = "Shift 3: Yesterday 09:00 PM to Today 08:00 AM (Overnight)"

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
