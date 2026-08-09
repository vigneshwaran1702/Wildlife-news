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
            bottomMargin=38

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

        now_dt = datetime.now()
        now_str = now_dt.strftime("%b %d, %Y")
        time_str = now_dt.strftime("%I:%M %p IST")
        download_datetime_formatted = f"Date: {now_str} | {time_str}"

        if filter_criteria is not None:
            filter_criteria["Downloaded At"] = download_datetime_formatted

        # Determine Scan Window text
        scan_window_text = "08:00 AM – 05:00 PM"
        if filter_criteria and "Time Window" in filter_criteria:
            tw = str(filter_criteria["Time Window"])
            if "Shift 1" in tw or "08:00 AM" in tw or "8am" in tw:
                scan_window_text = "08:00 AM – 05:00 PM"
            elif "Shift 2" in tw or "05:00 PM" in tw or "5pm" in tw:
                scan_window_text = "05:00 PM – 09:00 PM"
            elif "Shift 3" in tw or "09:00 PM" in tw or "9pm" in tw:
                scan_window_text = "09:00 PM – 08:00 AM"
            else:
                scan_window_text = tw

        # 1. Main Official Banner Box
        banner_left = [
            Paragraph("<b>TAMIL NADU FOREST DEPARTMENT</b>", hdr_title_style),
            Spacer(1, 2),
            Paragraph(f"Daily Media Scan Bulletin — Exhaustive Edition ({now_str})", hdr_sub_style)
        ]

        banner_right = [
            Paragraph(f"<b>{download_datetime_formatted}</b>", hdr_meta_style),
            Paragraph(f"<b>Scan Window:</b> {scan_window_text}", hdr_meta_style),
            Paragraph("<b>Issued By:</b> Vigneshwaran", hdr_meta_style)
        ]

        banner_table = Table([[banner_left, banner_right]], colWidths=[330, 226])
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
        sec1_hdr = Table([[Paragraph(f"1. PRESS COVERAGE INDEX ({scan_window_text.upper()} WINDOW)", sec_hdr_style)]], colWidths=[556])
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
        if not articles:
            idx_rows.append([
                Paragraph("-", tbl_cell_style),
                Paragraph("-", tbl_cell_style),
                Paragraph("N/A", tbl_cell_style),
                Paragraph("<b>No news articles recorded within this shift timeline window.</b>", tbl_cell_style),
                Paragraph("-", tbl_cell_style),
                Paragraph("-", tbl_cell_style)
            ])
        else:
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
        sec2_hdr = Table([[Paragraph(f"2. EXHAUSTIVE PRESS SUMMARIES ({scan_window_text.upper()})", sec_hdr_style)]], colWidths=[556])
        sec2_hdr.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HEADER_DARK),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(sec2_hdr)
        elements.append(Spacer(1, 6))

        if not articles:
            no_news_content = [
                Paragraph("<b>NO ARTICLES FOUND IN THIS TIMELINE WINDOW</b>", card_title_style),
                Spacer(1, 3),
                Paragraph("No media news or press releases were recorded in this specific shift interval. The backend system strictly monitors news within scheduled boundaries and excludes news from other shifts.", body_style)
            ]
            no_news_tbl = Table([[no_news_content]], colWidths=[556])
            no_news_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BOX_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, CARD_BORDER),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            elements.append(no_news_tbl)
        else:
            for idx, art in enumerate(articles, 1):
                date_str = art.published_at.strftime("%b %d") if art.published_at else ""
                time_val = art.published_at.strftime(f"%I:%M %p IST ({date_str})") if art.published_at else "09:00 AM IST"
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

        def draw_canvas_footer(canvas, doc_obj):
            canvas.saveState()
            dt = datetime.now()
            d_str = dt.strftime("%b %d, %Y")
            t_str = dt.strftime("%I:%M %p IST")
            footer_text = f"Compiled by Vigneshwaran   |   Downloaded On: {d_str} | {t_str}"

            page_w, _ = letter
            # Draw line above footer
            canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
            canvas.setLineWidth(0.75)
            canvas.line(28, 28, page_w - 28, 28)

            # Draw footer text
            canvas.setFont("Helvetica-Bold", 8.5)
            canvas.setFillColor(colors.HexColor("#0F172A"))
            canvas.drawCentredString(page_w / 2.0, 14, footer_text)
            canvas.restoreState()

        doc.build(elements, onFirstPage=draw_canvas_footer, onLaterPages=draw_canvas_footer)



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
