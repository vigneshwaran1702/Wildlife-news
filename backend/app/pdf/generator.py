import os
from typing import List, Dict
from datetime import datetime
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.schemas import Article, PDFReport
from app.services.storage import db_storage

import html
import re

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
        filename = f"WildTN_Report_{report_id}.pdf"
        file_path = os.path.join(PDF_DIR, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        PRIMARY_EMERALD = colors.HexColor("#0B3B2B")
        GOLD_ACCENT = colors.HexColor("#D97706")
        DARK_TEXT = colors.HexColor("#1F2937")
        LIGHT_BG = colors.HexColor("#F3F4F6")
        ALERT_RED = colors.HexColor("#DC2626")

        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=PRIMARY_EMERALD,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'HeaderSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#4B5563"),
            alignment=TA_LEFT
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=PRIMARY_EMERALD,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=DARK_TEXT
        )

        bullet_style = ParagraphStyle(
            'Bullet',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#374151"),
            leftIndent=10
        )

        elements = []

        # 1. Header Banner
        header_data = [
            [
                Paragraph("<b>WILDTN-NEWS INTELLIGENCE DIGEST</b>", title_style),
                Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %b %Y')}<br/><b>Type:</b> {report_type}", subtitle_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[380, 160])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT')
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_EMERALD, spaceAfter=12))

        # 2. Executive Summary Metrics
        high_conflicts = sum(1 for a in articles if a.conflict_level == "High")
        districts_count = len(set(a.district for a in articles))
        species_set = set()
        for a in articles:
            species_set.update(a.species)

        metrics_data = [
            [
                Paragraph(f"<b>Total Articles:</b> {len(articles)}", body_style),
                Paragraph(f"<b>High Conflict Alerts:</b> <font color='red'>{high_conflicts}</font>", body_style),
                Paragraph(f"<b>Districts Active:</b> {districts_count}", body_style),
                Paragraph(f"<b>Key Species Mentioned:</b> {len(species_set)}", body_style),
            ]
        ]
        metrics_table = Table(metrics_data, colWidths=[135, 135, 135, 135])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 14))

        # 3. Articles Content List
        elements.append(Paragraph(f"<b>Reported Wildlife Incidents & News ({len(articles)})</b>", section_heading))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=GOLD_ACCENT, spaceAfter=10))

        for idx, art in enumerate(articles, 1):
            conflict_color = "#DC2626" if art.conflict_level == "High" else "#D97706" if art.conflict_level == "Medium" else "#059669"
            badge = f"<font color='{conflict_color}'><b>[{art.conflict_level.upper()} RISK]</b></font>"

            clean_title = safe_pdf_text(art.title_en)
            art_title = Paragraph(f"<b>{idx}. {clean_title}</b> {badge}", ParagraphStyle(
                'ArtTitle', parent=styles['Heading3'], fontSize=11, leading=14, textColor=PRIMARY_EMERALD
            ))
            elements.append(art_title)

            # Metadata line with direct source link
            safe_url = html.escape(art.source_url)
            safe_source = safe_pdf_text(art.source_name)
            source_link = f"<a href='{safe_url}' color='#059669'><u>{safe_source} (Read Full News Online)</u></a>"
            meta_str = f"<b>District:</b> {safe_pdf_text(art.district)} | <b>Category:</b> {safe_pdf_text(art.category)} | <b>Source:</b> {source_link} | <b>Species:</b> {', '.join(art.species)}"
            elements.append(Paragraph(meta_str, ParagraphStyle('Meta', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor("#4B5563"))))
            elements.append(Spacer(1, 4))

            # Summary Bullets
            if art.summary_en:
                for line in art.summary_en.split('\n'):
                    if line.strip():
                        clean_line = safe_pdf_text(line.strip())
                        elements.append(Paragraph(f"• {clean_line.lstrip('• ')}", bullet_style))

            # Tamil Title Reference
            if art.title_ta and art.title_ta != art.title_en:
                elements.append(Spacer(1, 2))
                clean_ta = safe_pdf_text(art.title_ta)
                elements.append(Paragraph(f"<i>Tamil Headline:</i> {clean_ta}", ParagraphStyle('TaTitle', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor("#4B5563"))))

            elements.append(Spacer(1, 10))
            elements.append(HRFlowable(width="100%", thickness=0.2, color=colors.HexColor("#E5E7EB"), spaceAfter=8))

        # 4. Footer & Signature
        elements.append(Spacer(1, 10))
        footer_text = Paragraph("<i>Generated automatically by WildTN-News Wildlife Intelligence Platform | State Forest & Conservation Digest</i>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#9CA3AF")))
        elements.append(footer_text)

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
