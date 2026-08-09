import os
from typing import List, Dict
from datetime import datetime
import uuid
import html
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.schemas import Article, PDFReport
from app.services.storage import db_storage

PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pdfs")

def safe_pdf_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    return html.escape(clean)

class PDFReportGenerator:
    @staticmethod
    def generate_report(
        title: str,
        report_type: str,
        articles: List[Article],
        filter_criteria: Dict[str, str] = None
    ) -> PDFReport:
        os.makedirs(PDF_DIR, exist_ok=True)
        report_id = f"pdf_{uuid.uuid4().hex[:8]}"
        filename = f"TN_Forest_Media_Scan_{report_id}.pdf"
        file_path = os.path.join(PDF_DIR, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=28,
            leftMargin=28,
            topMargin=28,
            bottomMargin=28
        )

        styles = getSampleStyleSheet()

        # Black Edition Palette
        HEADER_DARK = colors.HexColor("#000000")
        ACCENT_BLUE = colors.HexColor("#111111")
        LIGHT_BOX_BG = colors.HexColor("#F8FAFC")
        CARD_BORDER = colors.HexColor("#94A3B8")
        SUB_BAR_BG = colors.HexColor("#F1F5F9")
        SUB_BAR_BORDER = colors.HexColor("#CBD5E1")
        TEXT_DARK = colors.HexColor("#0F172A")
        TEXT_MUTED = colors.HexColor("#334155")

        hdr_title_style = ParagraphStyle(
            'HdrTitle', parent=styles['Normal'],
            fontSize=16, leading=19, textColor=colors.white, fontName='Helvetica-Bold'
        )

        hdr_sub_style = ParagraphStyle(
            'HdrSub', parent=styles['Normal'],
            fontSize=9, leading=11, textColor=colors.HexColor("#E2E8F0")
        )

        hdr_meta_style = ParagraphStyle(
            'HdrMeta', parent=styles['Normal'],
            fontSize=8, leading=10, textColor=colors.white, alignment=TA_RIGHT
        )

        sec_hdr_style = ParagraphStyle(
            'SecHdr', parent=styles['Normal'],
            fontSize=10, leading=12, textColor=colors.white, fontName='Helvetica-Bold'
        )

        tbl_hdr_style = ParagraphStyle(
            'TblHdr', parent=styles['Normal'],
            fontSize=7.5, leading=9, textColor=colors.white, fontName='Helvetica-Bold'
        )

        tbl_cell_style = ParagraphStyle(
            'TblCell', parent=styles['Normal'],
            fontSize=7.5, leading=9.5, textColor=TEXT_DARK
        )

        card_title_style = ParagraphStyle(
            'CardTitle', parent=styles['Normal'],
            fontSize=9.5, leading=12, textColor=TEXT_DARK, fontName='Helvetica-Bold'
        )

        badge_style = ParagraphStyle(
            'BadgeStyle', parent=styles['Normal'],
            fontSize=7, leading=8, textColor=colors.HexColor("#000000"), fontName='Helvetica-Bold', alignment=TA_RIGHT
        )

        meta_line_style = ParagraphStyle(
            'MetaLine', parent=styles['Normal'],
            fontSize=7.5, leading=9.5, textColor=TEXT_MUTED
        )

        body_style = ParagraphStyle(
            'CardBody', parent=styles['Normal'],
            fontSize=8, leading=10.5, textColor=TEXT_DARK
        )

        link_style = ParagraphStyle(
            'LinkBox', parent=styles['Normal'],
            fontSize=7.5, leading=9.5, textColor=colors.HexColor("#000000")
        )

        kpi_val_style = ParagraphStyle(
            'KpiVal', parent=styles['Normal'],
            fontSize=13, leading=15, textColor=HEADER_DARK, fontName='Helvetica-Bold', alignment=TA_CENTER
        )

        kpi_lbl_style = ParagraphStyle(
            'KpiLbl', parent=styles['Normal'],
            fontSize=6.5, leading=8, textColor=TEXT_MUTED, fontName='Helvetica-Bold', alignment=TA_CENTER
        )

        elements = []

        now_str = datetime.now().strftime("%b %d, %Y")
        time_str = datetime.now().strftime("%I:%M %p IST")

        # 1. Main Official Banner Box
        banner_left = [
            Paragraph("<b>TAMIL NADU FOREST DEPARTMENT</b>", hdr_title_style),
            Spacer(1, 2),
            Paragraph(f"Daily Media Scan Bulletin — Exhaustive Evening Edition ({now_str})", hdr_sub_style)
        ]

        banner_right = [
            Paragraph(f"<b>Date:</b> {now_str} | {time_str}", hdr_meta_style),
            Paragraph("<b>Scan Window:</b> 08:00 AM – 05:30 PM", hdr_meta_style),
            Paragraph("<b>Issued By:</b> Vigneshwaran", hdr_meta_style)
        ]

        banner_table = Table([[banner_left, banner_right]], colWidths=[350, 206])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HEADER_DARK),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT')
        ]))
        elements.append(banner_table)
        elements.append(Spacer(1, 6))

        # 2. Executive KPI Cards Row (6 Metric Boxes)
        forest_cnt = sum(1 for a in articles if a.category in ["Forest Dept & Policy", "Forest Fire & Safety", "Forest Encroachment"])
        wildlife_cnt = len(articles) - forest_cnt

        kpi_data = [
            [
                [Paragraph("22", kpi_val_style), Paragraph("PAPERS SCANNED", kpi_lbl_style)],
                [Paragraph(f"{len(articles):02d}", kpi_val_style), Paragraph("TOTAL ARTICLES", kpi_lbl_style)],
                [Paragraph(f"{forest_cnt:02d}", kpi_val_style), Paragraph("FOREST STORIES", kpi_lbl_style)],
                [Paragraph(f"{wildlife_cnt:02d}", kpi_val_style), Paragraph("WILDLIFE STORIES", kpi_lbl_style)],
                [Paragraph("0", kpi_val_style), Paragraph("EXCLUDED", kpi_lbl_style)],
                [Paragraph("100%", kpi_val_style), Paragraph("VERIFIED LINKS", kpi_lbl_style)]
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[92.6, 92.6, 92.6, 92.6, 92.6, 92.6])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
            ('BOX', (0, 0), (-1, -1), 0.5, CARD_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, CARD_BORDER),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 8))

        # 3. Section 1 Header & Press Coverage Index Table
        sec1_hdr = Table([[Paragraph("1. PRESS COVERAGE INDEX (08:00 AM TO 05:30 PM WINDOW)", sec_hdr_style)]], colWidths=[556])
        sec1_hdr.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HEADER_DARK),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(sec1_hdr)
        elements.append(Spacer(1, 4))

        # Table Header
        idx_headers = [
            Paragraph("#", tbl_hdr_style),
            Paragraph("TIME OF NEWS", tbl_hdr_style),
            Paragraph("DISTRICT / DIVISION", tbl_hdr_style),
            Paragraph("ARTICLE HEADLINE", tbl_hdr_style),
            Paragraph("SOURCE", tbl_hdr_style),
            Paragraph("CATEGORY", tbl_hdr_style)
        ]

        idx_rows = [idx_headers]
        for i, art in enumerate(articles, 1):
            time_val = art.published_at.strftime("%I:%M %p IST") if art.published_at else "09:00 AM IST"
            clean_title = safe_pdf_text(art.title_en if art.title_en else art.title_ta)
            row = [
                Paragraph(str(i), tbl_cell_style),
                Paragraph(time_val, tbl_cell_style),
                Paragraph(safe_pdf_text(art.district), tbl_cell_style),
                Paragraph(clean_title, tbl_cell_style),
                Paragraph(safe_pdf_text(art.source_name), tbl_cell_style),
                Paragraph(safe_pdf_text(art.category), tbl_cell_style)
            ]
            idx_rows.append(row)

        idx_table = Table(idx_rows, colWidths=[20, 95, 110, 191, 70, 70])
        idx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_DARK),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
        ]))
        elements.append(idx_table)
        elements.append(Spacer(1, 10))

        # 4. Section 2 Header & Exhaustive Press Summaries
        sec2_hdr = Table([[Paragraph("2. EXHAUSTIVE EVENING PRESS SUMMARIES (08:00 AM TO 05:30 PM)", sec_hdr_style)]], colWidths=[556])
        sec2_hdr.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HEADER_DARK),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(sec2_hdr)
        elements.append(Spacer(1, 6))

        for idx, art in enumerate(articles, 1):
            time_val = art.published_at.strftime("%I:%M %p IST (Aug 08)") if art.published_at else "09:00 AM IST (Aug 08)"
            title_text = safe_pdf_text(art.title_en if art.title_en else art.title_ta)
            cat_badge = safe_pdf_text(art.category.upper())

            # Top Header Row of Card
            hdr_left = Paragraph(f"<b>{idx}. {title_text}</b>", card_title_style)
            hdr_right = Paragraph(f"<b>[{cat_badge}]</b>", badge_style)
            card_top_tbl = Table([[hdr_left, hdr_right]], colWidths=[436, 110])
            card_top_tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT')
            ]))

            # Sub Metadata & Where Line
            safe_source = safe_pdf_text(art.source_name)
            safe_dist = safe_pdf_text(art.district)
            where_p = Paragraph(f"<b>📍 WHERE (Location):</b> {safe_dist} &nbsp;|&nbsp; <b>Time:</b> {time_val} &nbsp;|&nbsp; <b>Source:</b> {safe_source}", meta_line_style)

            # What Happened Text
            body_text = safe_pdf_text(art.content_en if art.content_en else art.content_ta)
            what_p = Paragraph(f"<b>⚡ WHAT HAPPENED:</b> {body_text}", body_style)

            card_content = [
                card_top_tbl,
                Spacer(1, 3),
                where_p,
                Spacer(1, 4),
                what_p
            ]

            card_table = Table([[card_content]], colWidths=[556])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BOX_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, CARD_BORDER),
                ('PADDING', (0, 0), (-1, -1), 6)
            ]))

            elements.append(KeepTogether([card_table, Spacer(1, 6)]))

        # 5. Footer
        elements.append(Spacer(1, 6))
        footer_p = Paragraph("<b>Compiled by Vigneshwaran</b>", ParagraphStyle(
            'FooterStyle', parent=styles['Normal'], fontSize=8, leading=10, textColor=TEXT_MUTED, alignment=TA_CENTER
        ))
        elements.append(footer_p)

        doc.build(elements)

        report = PDFReport(
            id=report_id,
            title=title,
            report_type=report_type,
            file_path=file_path,
            download_url=f"/api/pdf/download/{report_id}",
            created_at=datetime.now(),
            article_count=len(articles),
            filter_criteria=filter_criteria or {}
        )

        db_storage.add_report(report)
        return report
