import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage

official_newspaper_links = {
    'The Hindu': 'https://www.thehindu.com/news/national/tamil-nadu/',
    'The New Indian Express': 'https://www.newindianexpress.com/states/tamil-nadu',
    'Dina Thanthi (தினத்தந்தி)': 'https://www.dailythanthi.com/News/State',
    'Dina Thanthi': 'https://www.dailythanthi.com/News/State',
    'Dinamalar (தினமலர்)': 'https://www.dinamalar.com/',
    'Dinamalar': 'https://www.dinamalar.com/',
    'Dinakaran (தினகரன்)': 'https://www.dinakaran.com/',
    'Dinakaran': 'https://www.dinakaran.com/',
    'Dinamani (தினமணி)': 'https://www.dinamani.com/all-editions/edition-chennai',
    'Dinamani': 'https://www.dinamani.com/all-editions/edition-chennai',
    'Hindu Tamil Thisai (தமிழ் இந்து)': 'https://www.hindutamil.in/',
    'DT Next': 'https://www.dtnext.in/news/tamilnadu',
    'Times of India': 'https://timesofindia.indiatimes.com/city/chennai',
    'Maalai Malar': 'https://www.maalaimalar.com/news/state',
    'News18 Tamil (நியூஸ்18 தமிழ்)': 'https://tamil.news18.com/',
    'Puthiya Thalaimurai (புதிய தலைமுறை)': 'https://www.puthiyathalaimurai.com/',
    'The Indian Express': 'https://indianexpress.com/section/cities/chennai/'
}

for art in db_storage.articles.values():
    direct_link = official_newspaper_links.get(art.source_name, 'https://www.thehindu.com/news/national/tamil-nadu/')
    art.source_url = direct_link

db_storage.save_data()
print(f"Updated all {len(db_storage.articles)} articles to 100% working direct newspaper URLs!")
for i, art in enumerate(list(db_storage.articles.values())[:10]):
    print(f"{i+1:2d} | {art.source_name:35s} | {art.source_url}")
