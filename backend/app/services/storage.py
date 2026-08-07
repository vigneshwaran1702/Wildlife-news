import json
import os
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from app.models.schemas import Article, PDFReport, CollectorLog

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
ARTICLES_FILE = os.path.join(DATA_DIR, "articles.json")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")

class StorageService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.articles: Dict[str, Article] = {}
        self.reports: Dict[str, PDFReport] = {}
        self.logs: List[CollectorLog] = []
        self._load_data()

    def _load_data(self):
        if os.path.exists(ARTICLES_FILE):
            try:
                with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # Parse datetimes
                        item['published_at'] = datetime.fromisoformat(item['published_at'])
                        item['created_at'] = datetime.fromisoformat(item['created_at'])
                        art = Article(**item)
                        self.articles[art.id] = art
            except Exception as e:
                print(f"Error loading articles: {e}")

        if os.path.exists(REPORTS_FILE):
            try:
                with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        item['created_at'] = datetime.fromisoformat(item['created_at'])
                        rep = PDFReport(**item)
                        self.reports[rep.id] = rep
            except Exception as e:
                print(f"Error loading reports: {e}")

    def save_data(self):
        try:
            with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
                articles_list = [a.dict() for a in self.articles.values()]
                json.dump(articles_list, f, default=str, ensure_ascii=False, indent=2)
            with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
                reports_list = [r.dict() for r in self.reports.values()]
                json.dump(reports_list, f, default=str, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_article(self, article: Article) -> Article:
        self.articles[article.id] = article
        self.save_data()
        return article

    def get_article(self, article_id: str) -> Optional[Article]:
        return self.articles.get(article_id)

    def get_articles(
        self,
        category: Optional[str] = None,
        district: Optional[str] = None,
        conflict_level: Optional[str] = None,
        species: Optional[str] = None,
        search: Optional[str] = None,
        bookmarked_only: bool = False
    ) -> List[Article]:
        results = list(self.articles.values())
        
        if category and category != "All":
            results = [a for a in results if a.category.lower() == category.lower()]
        
        if district and district != "All":
            results = [a for a in results if district.lower() in a.district.lower()]
            
        if conflict_level and conflict_level != "All":
            results = [a for a in results if a.conflict_level.lower() == conflict_level.lower()]

        if species and species != "All":
            results = [a for a in results if any(species.lower() in s.lower() for s in a.species)]

        if bookmarked_only:
            results = [a for a in results if a.is_bookmarked]

        if search:
            query = search.lower()
            results = [
                a for a in results
                if query in a.title_en.lower()
                or query in (a.title_ta or "").lower()
                or query in a.content_en.lower()
                or query in (a.summary_en or "").lower()
                or any(query in tag.lower() for tag in a.tags)
            ]

        # Sort by published_at descending
        results.sort(key=lambda x: x.published_at, reverse=True)
        return results

    def toggle_bookmark(self, article_id: str) -> Optional[Article]:
        if article_id in self.articles:
            self.articles[article_id].is_bookmarked = not self.articles[article_id].is_bookmarked
            self.save_data()
            return self.articles[article_id]
        return None

    def add_report(self, report: PDFReport) -> PDFReport:
        self.reports[report.id] = report
        self.save_data()
        return report

    def get_reports(self) -> List[PDFReport]:
        reports = list(self.reports.values())
        reports.sort(key=lambda x: x.created_at, reverse=True)
        return reports

    def add_log(self, log: CollectorLog):
        self.logs.insert(0, log)
        if len(self.logs) > 100:
            self.logs = self.logs[:100]

    def get_logs(self) -> List[CollectorLog]:
        return self.logs

db_storage = StorageService()
