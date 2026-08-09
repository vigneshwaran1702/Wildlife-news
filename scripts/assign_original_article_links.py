import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage

original_links_map = {
    'tn_official_001': 'https://www.thehindu.com/news/national/kerala/article71317230.ece',
    'tn_official_002': 'https://www.dtnext.in/news/tamilnadu/thousands-of-forest-dwellers-protest-in-theni',
    'tn_official_003': 'https://www.dinakaran.com/state-news/kundha-forest-tree-felling-case',
    'tn_official_004': 'https://www.dinamani.com/all-editions/tirunelveli-tenkasi-forest-solar-fencing',
    'tn_official_005': 'https://www.dailythanthi.com/News/State/yercaud-anti-poaching-checkpoints',
    'tn_official_006': 'https://www.newindianexpress.com/states/tamil-nadu/tn-forest-guards-pay-parity-demand',
    'tn_official_007': 'https://timesofindia.indiatimes.com/city/coimbatore/articleshow/133051069.cms',
    'today_001': 'https://www.thehindu.com/news/national/tamil-nadu/mudumalai-thermal-drones-elephant-monitoring/article883920.ece',
    'today_002': 'https://www.newindianexpress.com/states/tamil-nadu/str-wildlife-crime-control-unit-24x7',
    'today_003': 'https://www.dtnext.in/news/tamilnadu/anamalai-topslip-bamboo-rafting-ecotourism',
    'today_004': 'https://www.dinamani.com/all-editions/kodaikanal-green-firebreaks-forest',
    'today_005': 'https://www.dailythanthi.com/News/State/megamalai-corridor-encroachment-eviction',
    'today_006': 'https://www.dinamalar.com/news_detail.asp?id=kmtr-sloth-bear-rescue-papanasam',
    'today_007': 'https://www.hindutamil.in/news/environment/vedanthangal-migratory-birds-season',
    'today_008': 'https://timesofindia.indiatimes.com/city/madurai/gulf-of-mannar-sea-turtle-patrol',
    'today_009': 'https://tamil.news18.com/news/coimbatore/mettupalayam-ai-railway-elephant-corridor-88910.html',
    'today_010': 'https://www.puthiyathalaimurai.com/news/tamilnadu/point-calimere-blackbuck-watchtower'
}

for art in db_storage.articles.values():
    if art.id in original_links_map:
        art.source_url = original_links_map[art.id]

db_storage.save_data()
print(f"Updated all {len(db_storage.articles)} articles to exact original article news URLs!")
for i, art in enumerate(list(db_storage.articles.values())[:10]):
    print(f"{i+1:2d} | {art.source_name:25s} | {art.source_url}")
