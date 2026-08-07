from fastapi import APIRouter
from collections import Counter
from app.models.schemas import AnalyticsOverview
from app.services.storage import db_storage

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsOverview)
def get_analytics():
    articles = list(db_storage.articles.values())
    total = len(articles)

    high_c = sum(1 for a in articles if a.conflict_level == "High")
    med_c = sum(1 for a in articles if a.conflict_level == "Medium")
    low_c = sum(1 for a in articles if a.conflict_level in ["Low", "None"])

    # District counts
    district_counts = Counter(a.district for a in articles)
    top_districts = [{"district": k, "count": v} for k, v in district_counts.most_common(7)]

    # Species counts
    species_counter = Counter()
    for a in articles:
        for s in a.species:
            species_counter[s] += 1
    top_species = [{"species": k, "count": v} for k, v in species_counter.most_common(7)]

    # Category breakdown
    cat_counts = Counter(a.category for a in articles)
    category_distribution = [{"category": k, "count": v} for k, v in cat_counts.items()]

    # Trend (simulated last 7 days)
    recent_trend = [
        {"day": "Mon", "conflicts": max(1, high_c // 2), "total": max(2, total // 5)},
        {"day": "Tue", "conflicts": max(2, high_c // 3), "total": max(3, total // 4)},
        {"day": "Wed", "conflicts": max(1, high_c // 4), "total": max(2, total // 5)},
        {"day": "Thu", "conflicts": max(3, high_c // 2), "total": max(4, total // 3)},
        {"day": "Fri", "conflicts": high_c, "total": total},
    ]

    return AnalyticsOverview(
        total_articles=total,
        high_conflict_count=high_c,
        medium_conflict_count=med_c,
        low_conflict_count=low_c,
        top_districts=top_districts,
        top_species=top_species,
        category_distribution=category_distribution,
        recent_trend=recent_trend
    )
