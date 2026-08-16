import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.collectors.pipeline import ArticlePipeline
from app.services.storage import db_storage

IST = ZoneInfo("Asia/Kolkata")
today = datetime.now(IST).date()
three_days_ago = today - timedelta(days=3)

print("==================================================")
print("TESTING ARTICLE PIPELINE STRICT FILTERING FLOW")
print(f"Today's date (IST): {today}")
print("==================================================")

# Test 1: Date Filter Check (Older than 36h article => REJECT)
raw_old = {"published": three_days_ago.strftime("%Y-%m-%d 10:00:00")}
res_old = ArticlePipeline.process_article(
    raw_entry=raw_old,
    title="Old News: Elephant spotted in Mudumalai forest range",
    content="A wild elephant was spotted moving in Mudumalai.",
    link="https://example.com/old_01",
    source_name="The Hindu"
)
print(f"Test 1 (Old Date Filter): Expected None, Got: {res_old}")
assert res_old is None, "Failed: Old article was not rejected by Date Filter!"

# Test 2: Location Filter Check (Delhi news => REJECT)
raw_today_delhi = {"published": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")}
res_delhi = ArticlePipeline.process_article(
    raw_entry=raw_today_delhi,
    title="Delhi Traffic Police issue smog advisory",
    content="Delhi authorities have issued a smog alert for northern roads.",
    link="https://example.com/delhi_01",
    source_name="Times of India"
)
print(f"Test 2 (Location Filter): Expected None, Got: {res_delhi}")
assert res_delhi is None, "Failed: Non-TN article was not rejected by Location Filter!"

# Test 3: Topic Filter Check (TN Politics => REJECT)
raw_today_politics = {"published": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")}
res_politics = ArticlePipeline.process_article(
    raw_entry=raw_today_politics,
    title="Tamil Nadu Assembly debates municipal budget allocation",
    content="State ministers discussed city infrastructure budget in Chennai.",
    link="https://example.com/tn_politics_01",
    source_name="Dina Thanthi"
)
print(f"Test 3 (Topic Filter): Expected None, Got: {res_politics}")
assert res_politics is None, "Failed: Non-wildlife TN article was not rejected by Topic Filter!"

# Test 4: Valid TODAY Tamil Nadu Forest/Wildlife Article => ACCEPT
raw_valid_today = {"published": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")}
res_valid = ArticlePipeline.process_article(
    raw_entry=raw_valid_today,
    title="TN Forest Department deploys AI camera towers along Coimbatore elephant corridor",
    content="Coimbatore Forest Division installed 10 thermal sensor warning sirens to protect wild elephant herds from train tracks.",
    link="https://example.com/valid_today_01",
    source_name="The Hindu"
)
print(f"Test 4 (Valid TODAY Article): Got Article ID = {res_valid.id if res_valid else None}, Title = {res_valid.title_en if res_valid else None}")
assert res_valid is not None, "Failed: Valid TODAY TN wildlife article was rejected!"
assert res_valid.date_status == "TODAY", "Failed: Article date_status is not TODAY!"

print("\nAll ArticlePipeline tests PASSED successfully!")
