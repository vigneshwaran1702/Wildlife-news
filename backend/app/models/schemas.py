from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class KeyEntities(BaseModel):
    locations: List[str] = Field(default_factory=list)
    species: List[str] = Field(default_factory=list)
    authorities: List[str] = Field(default_factory=list)
    impact: Optional[str] = ""

class ArticleBase(BaseModel):
    title_en: str
    title_ta: Optional[str] = ""
    content_en: str
    content_ta: Optional[str] = ""
    summary_en: Optional[str] = ""
    summary_ta: Optional[str] = ""
    category: str = "General Wildlife"  # Human-Wildlife Conflict, Rescue & Rehabilitation, Forest Dept & Policy, Species Conservation, Anti-Poaching, Eco-Tourism
    conflict_level: str = "Low"  # High, Medium, Low, None
    district: str = "Tamil Nadu"  # Coimbatore, Nilgiris, Sathyamangalam, Anamalai, Mudumalai, Kanyakumari, etc.
    species: List[str] = Field(default_factory=list)  # Elephant, Tiger, Leopard, Gaur, Wild Boar, etc.
    source_name: str
    source_url: str
    published_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    key_entities: Optional[KeyEntities] = Field(default_factory=KeyEntities)
    sentiment: str = "Neutral"  # Positive, Neutral, Negative, Critical Alert
    date_status: str = "TODAY"  # TODAY, YESTERDAY, OLD

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
    views_count: int = 0
    is_bookmarked: bool = False

class PDFReport(BaseModel):
    id: str
    title: str
    report_type: str  # Daily Bulletin, Conflict Briefing, Weekly Digest
    file_path: str
    download_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    article_count: int = 0
    filter_criteria: Dict[str, str] = Field(default_factory=dict)

class CollectorLog(BaseModel):
    id: str
    collector_name: str
    status: str  # Success, Running, Warning, Error
    articles_found: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
    log_message: str

class AnalyticsOverview(BaseModel):
    total_articles: int
    high_conflict_count: int
    medium_conflict_count: int
    low_conflict_count: int
    top_districts: List[Dict[str, Any]]
    top_species: List[Dict[str, Any]]
    category_distribution: List[Dict[str, Any]]
    recent_trend: List[Dict[str, Any]]
