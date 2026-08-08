import os

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

    if not articles:
        articles = db_storage.get_articles()[:10]  # Fallback to top 10

    filter_dict = {
        "Category": payload.category or "All",
        "District": payload.district or "All",
        "Conflict Level": payload.conflict_level or "All"
    }

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
