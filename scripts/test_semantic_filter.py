import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.ai.classifier import is_tamil_nadu, is_wildlife_or_forest, ArticleClassifier
from app.collectors.pipeline import ArticlePipeline
from app.models.schemas import Article

IST = ZoneInfo("Asia/Kolkata")
now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

print("==================================================")
print("TESTING SEMANTIC WILDLIFE & TAMIL NADU CLASSIFIER")
print("==================================================")

# 1. Test is_tamil_nadu with various inputs
tn_article_1 = {"title": "Wild elephant herd spotted near Valparai tea estate", "content": "Forest department squad deployed."}
tn_article_2 = "நீலகிரி வனப்பகுதியில் சிறுத்தை நடமாட்டம் அதிகரிப்பு"
non_tn_article = {"title": "Delhi High Court issues pollution guidelines", "content": "Capital city traffic police."}

assert is_tamil_nadu(tn_article_1) == True, "Failed: TN article 1 (Valparai) should be TN relevant!"
assert is_tamil_nadu(tn_article_2) == True, "Failed: TN article 2 (Tamil script Nilgiris) should be TN relevant!"
assert is_tamil_nadu(non_tn_article) == False, "Failed: Delhi article should NOT be TN relevant!"
print("✔ is_tamil_nadu() tests PASSED!")

# 2. Test is_wildlife_or_forest semantic classification
sem_wildlife_1 = {
    "title": "Thermal warning sirens installed on rail line to safeguard pachyderms from trains",
    "content": "Anti-poaching squad installed AI camera towers to track animal movement near tracks."
}
sem_wildlife_2 = {
    "title": "Gulf of Mannar marine reserve launch for Dugong habitat conservation",
    "content": "Seagrass restoration initiative protecting endangered sea cows."
}
sem_wildlife_3 = {
    "title": "Pangolin scale contraband seized by wildlife crime control bureau",
    "content": "Two suspects arrested under Wildlife Protection Act for illegal animal trade."
}
non_wildlife_tn = {
    "title": "Tamil Nadu IT minister inaugurates new tech park in Chennai",
    "content": "Software companies expand operational hubs."
}
non_wildlife_farm = {
    "title": "Agricultural ministry announces PPFM spraying and fertilizer subsidy for paddy crops",
    "content": "Farmers receive sugarcane price bonus."
}

assert is_wildlife_or_forest(sem_wildlife_1) == True, "Failed: Pachyderm rail warning sirens should be semantically wildlife relevant!"
assert is_wildlife_or_forest(sem_wildlife_2) == True, "Failed: Dugong marine conservation should be semantically wildlife relevant!"
assert is_wildlife_or_forest(sem_wildlife_3) == True, "Failed: Pangolin crime bust should be semantically wildlife relevant!"
assert is_wildlife_or_forest(non_wildlife_tn) == False, "Failed: Tech park inauguration should NOT be wildlife relevant!"
assert is_wildlife_or_forest(non_wildlife_farm) == False, "Failed: Pure farm spraying should NOT be wildlife relevant!"
print("✔ is_wildlife_or_forest() semantic tests PASSED!")

# 3. Test Pipeline Control Flow (if is_tamil_nadu(article) and is_wildlife_or_forest(article): include_article() else: reject_article())
raw_valid = {"published": now_str}
res_valid = ArticlePipeline.process_article(
    raw_entry=raw_valid,
    title="Sathyamangalam Tiger Reserve deploys drone cameras for elephant migration tracking",
    content="Forest officers monitored animal herd crossing Bhavanisagar range.",
    link="https://example.com/str_drone_01",
    source_name="The Hindu",
    verify_web_source=False
)
assert res_valid is not None, "Failed: Valid TN Wildlife article rejected by pipeline!"

raw_rejected_tn_only = {"published": now_str}
res_rejected_tn_only = ArticlePipeline.process_article(
    raw_entry=raw_rejected_tn_only,
    title="Chennai Corporation announces municipal road expansion budget",
    content="Civic body allocates funds for traffic signals.",
    link="https://example.com/chennai_road_01",
    source_name="Times of India",
    verify_web_source=False
)
assert res_rejected_tn_only is None, "Failed: Non-wildlife TN article should have been rejected by pipeline!"

raw_rejected_wildlife_only = {"published": now_str}
res_rejected_wildlife_only = ArticlePipeline.process_article(
    raw_entry=raw_rejected_wildlife_only,
    title="Kaziranga National Park anti-poaching team arrests rhino horn smugglers in Assam",
    content="Assam forest guard seized illegal contraband.",
    link="https://example.com/kaziranga_01",
    source_name="Assam Tribune",
    verify_web_source=False
)
assert res_rejected_wildlife_only is None, "Failed: Out-of-state wildlife article should have been rejected by pipeline!"

print("✔ ArticlePipeline filter flow (is_tamil_nadu and is_wildlife_or_forest) tests PASSED!")
print("\nALL SEMANTIC FILTER TESTS PASSED SUCCESSFULLY!")
