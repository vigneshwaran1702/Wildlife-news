import os
from datetime import datetime, timedelta, time

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.models.schemas import PDFReport
from app.pdf.generator import PDFReportGenerator
from app.services.storage import db_storage

router = APIRouter(prefix="/api/pdf", tags=["PDF Reports"])

class PDFGenerateRequest(BaseModel):
    title: Optional[str] = None
    report_type: str = "Custom Briefing"
    shift_id: Optional[int] = None
    target_date: Optional[str] = None
    category: Optional[str] = None
    district: Optional[str] = None
    conflict_level: Optional[str] = None

from app.scheduler.jobs import scheduler

def make_naive(dt: Any) -> datetime:
    if dt is None:
        return datetime.now()
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return datetime.now()
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt if isinstance(dt, datetime) else datetime.now()

def generate_shift_pdf_by_id(shift_id: int, target_date: Optional[str] = None) -> PDFReport:
    now = datetime.now()
    if target_date:
        try:
            ref_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            ref_date = now.date()
    else:
        ref_date = now.date()

    all_articles = db_storage.get_articles()

    if shift_id == 1:
        # Shift 1: Day Bulletin (08:00 AM - 05:00 PM) on ref_date
        start_time = datetime.combine(ref_date, time(8, 0, 0))
        end_time = datetime.combine(ref_date, time(17, 0, 0))
        articles = [
            a for a in all_articles
            if a.published_at and start_time <= make_naive(a.published_at) <= end_time
        ]

        title = f"Shift 1 Day Bulletin (8:00 AM - 5:00 PM) - {ref_date.strftime('%d %b %Y')}"
        report_type = "Shift 1: Day Bulletin (08:00 AM - 05:00 PM)"
        filter_criteria = {
            "Time Window": f"{ref_date.strftime('%b %d, %Y')} 08:00 AM to 05:00 PM",
            "Deduplication": "Excludes Evening (5pm-9pm) & Night (9pm-8am) News",
            "Auto Schedule": "17:00 (5:00 PM) Daily Trigger",
            "Endpoint": f"/api/pdf/trigger-shift/1?target_date={ref_date.strftime('%Y-%m-%d')}"
        }
    elif shift_id == 2:
        # Shift 2: Evening Bulletin (05:00 PM - 09:00 PM) on ref_date
        start_time = datetime.combine(ref_date, time(17, 0, 0))
        end_time = datetime.combine(ref_date, time(21, 0, 0))
        articles = [
            a for a in all_articles
            if a.published_at and start_time <= make_naive(a.published_at) <= end_time
        ]

        title = f"Shift 2 Evening Bulletin (5:00 PM - 9:00 PM) - {ref_date.strftime('%d %b %Y')}"
        report_type = "Shift 2: Evening Bulletin (05:00 PM - 09:00 PM)"
        filter_criteria = {
            "Time Window": f"{ref_date.strftime('%b %d, %Y')} 05:00 PM to 09:00 PM",
            "Deduplication": "Excludes Shift 1 (8am-5pm) & Night (9pm-8am) News",
            "Auto Schedule": "21:00 (9:00 PM) Daily Trigger",
            "Endpoint": f"/api/pdf/trigger-shift/2?target_date={ref_date.strftime('%Y-%m-%d')}"
        }
    elif shift_id == 3:
        # Shift 3: Night & Early Morning Bulletin (09:00 PM yesterday to 08:00 AM on ref_date)
        start_time = datetime.combine(ref_date - timedelta(days=1), time(21, 0, 0))
        end_time = datetime.combine(ref_date, time(8, 0, 0))
        articles = [
            a for a in all_articles
            if a.published_at and start_time <= make_naive(a.published_at) <= end_time
        ]

        title = f"Shift 3 Night & Early Morning Bulletin (9:00 PM - 8:00 AM) - {ref_date.strftime('%d %b %Y')}"
        report_type = "Shift 3: Night & Early Morning Bulletin (09:00 PM - 08:00 AM)"
        filter_criteria = {
            "Time Window": f"{(ref_date - timedelta(days=1)).strftime('%b %d 09:00 PM')} to {ref_date.strftime('%b %d 08:00 AM')}",
            "Deduplication": "Excludes Daytime (8am-5pm) & Evening (5pm-9pm) News",
            "Auto Schedule": "08:00 (8:00 AM) Daily Trigger",
            "Endpoint": f"/api/pdf/trigger-shift/3?target_date={ref_date.strftime('%Y-%m-%d')}"
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
def trigger_shift_pdf(shift_id: int, target_date: Optional[str] = Query(None), as_json: bool = False):
    try:
        report = generate_shift_pdf_by_id(shift_id, target_date=target_date)

        if as_json:
            return report

        if not report.file_path or not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail=f"Generated PDF file not found at path '{report.file_path}'")

        filename = os.path.basename(report.file_path)
        return FileResponse(
            report.file_path,
            media_type="application/pdf",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF Generation Error: {str(e)}")

@router.get("/reports", response_model=List[PDFReport])
def list_pdf_reports():
    return db_storage.get_reports()

@router.delete("/clear-history")
@router.post("/clear-history")
def clear_pdf_history():
    db_storage.clear_reports()
    return {"status": "Success", "message": "PDF reports history cleared successfully"}

@router.post("/generate", response_model=PDFReport)
def generate_pdf_report(payload: PDFGenerateRequest):
    rt = (payload.report_type or "").lower()

    if payload.shift_id in [1, 2, 3]:
        return generate_shift_pdf_by_id(payload.shift_id, target_date=payload.target_date)
    elif "shift 1" in rt or "shift1" in rt or "8am-5pm" in rt:
        return generate_shift_pdf_by_id(1, target_date=payload.target_date)
    elif "shift 2" in rt or "shift2" in rt or "5pm-9pm" in rt:
        return generate_shift_pdf_by_id(2, target_date=payload.target_date)
    elif "shift 3" in rt or "shift3" in rt or "9pm-8am" in rt:
        return generate_shift_pdf_by_id(3, target_date=payload.target_date)

    articles = db_storage.get_articles(
        category=payload.category,
        district=payload.district,
        conflict_level=payload.conflict_level
    )

    filter_dict = {
        "Category": payload.category or "All",
        "District": payload.district or "All",
        "Risk Level": payload.conflict_level or "All"
    }

    title = payload.title or f"{payload.report_type} - {datetime.now().strftime('%d %b %Y')}"

    return PDFReportGenerator.generate_report(
        title=title,
        report_type=payload.report_type,
        articles=articles,
        filter_criteria=filter_dict
    )

from app.pdf.generator import PDF_DIR

def resolve_pdf_file_path(report_id: str, report: Optional[PDFReport] = None) -> str:
    # 1. Try provided report object file_path if valid
    if report and report.file_path and os.path.exists(report.file_path):
        return report.file_path

    # 2. Clean report_id
    clean_id = report_id.replace(".pdf", "")
    if clean_id.startswith("TN_Forest_Media_Scan_"):
        clean_id = clean_id.replace("TN_Forest_Media_Scan_", "")

    # Look up report by clean_id if not provided
    if not report:
        report = db_storage.reports.get(clean_id)
        if report and report.file_path and os.path.exists(report.file_path):
            return report.file_path

    # 3. Check standard expected filename in PDF_DIR
    target_filename = f"TN_Forest_Media_Scan_{clean_id}.pdf"
    target_path = os.path.join(PDF_DIR, target_filename)
    if os.path.exists(target_path):
        return target_path

    # 4. Search PDF_DIR for any file containing clean_id
    if os.path.exists(PDF_DIR):
        for fname in os.listdir(PDF_DIR):
            if clean_id in fname and fname.endswith(".pdf"):
                return os.path.join(PDF_DIR, fname)

    raise HTTPException(status_code=404, detail=f"PDF report file for ID '{report_id}' not found on server")

@router.get("/download/{report_id}")
def download_pdf(report_id: str):
    report = db_storage.reports.get(report_id)
    file_path = resolve_pdf_file_path(report_id, report)
    filename = os.path.basename(file_path)
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@router.get("/view/{report_id}")
def view_pdf(report_id: str):
    report = db_storage.reports.get(report_id)
    file_path = resolve_pdf_file_path(report_id, report)
    filename = os.path.basename(file_path)
    return FileResponse(
        file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{filename}\""}
    )


