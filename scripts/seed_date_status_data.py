import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage
from app.models.schemas import Article, KeyEntities

now = datetime.now()
today = now.date()
yesterday = today - timedelta(days=1)
older_date = today - timedelta(days=3)

status_articles = [
    # TODAY Shift 1 (08:00 AM - 05:00 PM)
    {
        "id": "status_today_001",
        "title_en": "TN Forest Department deploys AI thermal sensors along Coimbatore railway corridor",
        "title_ta": "தமிழ்நாடு வனத்துறை கோவை ரயில் பாதையில் AI வெப்ப உணரிகளை நிறுவியது",
        "content_en": "The Tamil Nadu Forest Department installed 10 high-resolution thermal sensors along Mettupalayam rail line to alert train pilots when wild elephant herds cross.",
        "content_ta": "கோவை மேட்டுப்பாளையம் ரயில் பாதையில் காட்டு யானைகள் கடக்கும் போது ரயில் ஓட்டுநர்களை எச்சரிக்க 10 AI வெப்ப உணரிகளை தமிழ்நாடு வனத்துறை நிறுவியுள்ளது.",
        "category": "Human-Wildlife Conflict",
        "district": "Coimbatore",
        "species": ["Elephant"],
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/coimbatore-ai-railway-elephant-corridor",
        "time": datetime.combine(today, datetime.min.time()).replace(hour=8, minute=30),
        "date_status": "TODAY"
    },
    {
        "id": "status_today_002",
        "title_en": "TNFWCCB seizes illegal sandalwood timber during highway check in Salem",
        "title_ta": "சேலத்தில் TNFWCCB சோதனை: சட்டவிரோத சந்தன மரங்கள் பறிமுதல்",
        "content_en": "Tamil Nadu Forest Wildlife Crime Control Bureau (TNFWCCB) officers intercepted a commercial vehicle transporting contraband sandalwood near Yercaud ghat road.",
        "content_ta": "தமிழ்நாடு வனவிலங்கு குற்றத் தடுப்புப் பிரிவு (TNFWCCB) அதிகாரிகள் ஏற்காடு மலைப்பாதையில் சட்டவிரோத சந்தனக் கட்டைகளைக் கடத்திச் சென்ற வாகனத்தைப் பறிமுதல் செய்தனர்.",
        "category": "Wildlife Crime & Rescue",
        "district": "Salem & Yercaud",
        "species": ["Sandalwood"],
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State/salem-tnfwccb-sandalwood-seizure",
        "time": datetime.combine(today, datetime.min.time()).replace(hour=9, minute=15),
        "date_status": "TODAY"
    },

    # TODAY Shift 2 (05:00 PM - 09:00 PM)
    {
        "id": "status_today_shift2_001",
        "title_en": "Anamalai Tiger Reserve issues night travel advisory along Valparai ghat road due to elephant herd movement",
        "title_ta": "ஆனைமலை புலிகள் காப்பகம் வால்பாறை மலைப்பாதையில் இரவு நேர பயண ஆலோசனையை வெளியிட்டுள்ளது",
        "content_en": "Forest officials at Anamalai Tiger Reserve advised evening motorists to exercise extreme caution as a herd of 8 wild elephants crossed the Valparai ghat highway.",
        "content_ta": "வால்பாறை மலைப்பாதையில் 8 காட்டு யானைகள் கடப்பதால் மாலை நேர வாகன ஓட்டிகள் மிகுந்த எச்சரிக்கையுடன் இருக்குமாறு வனத்துறை அதிகாரிகள் அறிவுறுத்தியுள்ளனர்.",
        "category": "Human-Wildlife Conflict",
        "district": "Anamalai",
        "species": ["Elephant"],
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/anamalai-elephant-travel-advisory",
        "time": datetime.combine(today, datetime.min.time()).replace(hour=18, minute=20),
        "date_status": "TODAY"
    },
    {
        "id": "status_today_shift2_002",
        "title_en": "TN Forest Department team tranquilizes and relocates stray gaur near Kodaikanal foothills",
        "title_ta": "கொடைக்கானல் அடிவாரத்தில் சுற்றிய காட்டெருமையை தமிழ்நாடு வனத்துறை மயக்க ஊசி செலுத்தி பிடித்தது",
        "content_en": "A specialized veterinary team of the Tamil Nadu Forest Department successfully tranquilized an adult male gaur that wandered into residential orchards near Kodaikanal.",
        "content_ta": "கொடைக்கானல் அருகே குடியிருப்பு பகுதிக்குள் புகுந்த காட்டெருமையை தமிழ்நாடு வனத்துறை மருத்துவ குழு மயக்க ஊசி செலுத்தி வெற்றிகரமாக பிடித்தது.",
        "category": "Wildlife Crime & Rescue",
        "district": "Dindigul & Kodaikanal",
        "species": ["Gaur"],
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State/kodaikanal-gaur-rescue-relocation",
        "time": datetime.combine(today, datetime.min.time()).replace(hour=20, minute=10),
        "date_status": "TODAY"
    },

    # TODAY Shift 3 (Yesterday 09:00 PM - Today 08:00 AM)
    {
        "id": "status_today_shift3_001",
        "title_en": "Early morning forest squad safely herds wild tusker back into Mudumalai reserve core",
        "title_ta": "அதிகாலை வன ரோந்துப் படை காட்டு யானையை பாதுகாப்பாக முதுமலை வனப்பகுதிக்குள் விரட்டியது",
        "content_en": "At 3:30 AM today, Mudumalai night patrol teams spotted a single wild tusker near Masinagudi border and safely guided the animal back into deep forest.",
        "content_ta": "இன்று அதிகாலை 3:30 மணிக்கு மசினகுடி எல்லை அருகே வந்த காட்டு யானையை முதுமலை இரவு ரோந்துப் படையினர் பாதுகாப்பாக காட்டுக்குள் திருப்பினார்கள்.",
        "category": "Human-Wildlife Conflict",
        "district": "Nilgiris",
        "species": ["Elephant"],
        "source": "The New Indian Express",
        "url": "https://www.newindianexpress.com/states/tamil-nadu/mudumalai-early-morning-elephant-patrol",
        "time": datetime.combine(today, datetime.min.time()).replace(hour=3, minute=30),
        "date_status": "TODAY"
    },
    {
        "id": "status_today_shift3_002",
        "title_en": "Night monitoring team intercepts illegal timber truck along Thenpennai river forest belt",
        "title_ta": "தென்பெண்ணை ஆற்று வனப்பகுதியில் இரவு கண்காணிப்பு குழு சட்டவிரோத மர லாரியை பிடித்தது",
        "content_en": "During overnight patrolling at 10:45 PM yesterday, Tamil Nadu forest squads impounded a timber-laden truck attempting illegal transit.",
        "content_ta": "நேற்று இரவு 10:45 மணிக்கு மேற்கொண்ட ரோந்தின் போது சட்டவிரோதமாக மரம் ஏற்றிச் சென்ற லாரியை வனத்துறை அதிகாரிகள் பறிமுதல் செய்தனர்.",
        "category": "Wildlife Crime & Rescue",
        "district": "Dharmapuri & Krishnagiri",
        "species": ["Teak Wood"],
        "source": "Dinamalar (தினமலர்)",
        "url": "https://www.dinamalar.com/news/state/thenpennai-night-timber-seizure",
        "time": datetime.combine(yesterday, datetime.min.time()).replace(hour=22, minute=45),
        "date_status": "YESTERDAY"
    },

    # YESTERDAY (Aug 8, 2026)
    {
        "id": "status_yesterday_001",
        "title_en": "Mudumalai Tiger Reserve deploys thermal drones to monitor wild elephant herd near Masinagudi",
        "title_ta": "மசினகுடி அருகே காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பகம் வெப்ப ட்ரோன்களை இயக்கியது",
        "content_en": "Forest officials in Mudumalai Tiger Reserve activated high-resolution thermal drones to track 14 wild elephants near Masinagudi.",
        "content_ta": "மசினகுடி அருகே நகரும் 14 காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பக வனத்துறையினர் ட்ரோன்களை இயக்கியுள்ளனர்.",
        "category": "Human-Wildlife Conflict",
        "district": "Nilgiris",
        "species": ["Elephant"],
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/mudumalai-thermal-drones-elephant-monitoring",
        "time": datetime.combine(yesterday, datetime.min.time()).replace(hour=14, minute=20),
        "date_status": "YESTERDAY"
    },
    {
        "id": "status_yesterday_002",
        "title_en": "TN Forest Department establishes 24x7 Wildlife Crime Control Unit in Sathyamangalam Tiger Reserve",
        "title_ta": "சத்தியமங்கலம் புலிகள் காப்பகத்தில் 24 மணி நேர வனக்குற்ற கட்டுப்பாட்டு மையத்தை அமைத்தது தமிழ்நாடு வனத்துறை",
        "content_en": "To prevent poaching and illegal timber trafficking along interstate border, Sathyamangalam Tiger Reserve set up a 24x7 control unit.",
        "content_ta": "வேட்டையாடுதல் மற்றும் மரக் கடத்தலைத் தடுக்க சத்தியமங்கலம் புலிகள் காப்பகத்தில் 24 மணி நேர வனக்குற்ற கட்டுப்பாட்டு மையம் அமைக்கப்பட்டது.",
        "category": "Wildlife Crime & Rescue",
        "district": "Erode & Sathyamangalam",
        "source": "The New Indian Express",
        "url": "https://www.newindianexpress.com/states/tamil-nadu/str-wildlife-crime-control-unit-24x7",
        "species": ["Tiger", "Elephant"],
        "time": datetime.combine(yesterday, datetime.min.time()).replace(hour=16, minute=45),
        "date_status": "YESTERDAY"
    },

    # OLD (Aug 6, 2026)
    {
        "id": "status_old_001",
        "title_en": "Madras High Court orders strict eviction of resort encroachments in Megamalai elephant corridor",
        "title_ta": "மேகமலை யானை வழித்தட விடுதி ஆக்கிரமிப்புகளை உடனடியாக அகற்ற சென்னை உயர்நீதிமன்றம் உத்தரவு",
        "content_en": "The Madras High Court bench directed Theni district administration and Forest Department to clear commercial resort encroachments obstructing Megamalai corridor.",
        "content_ta": "மேகமலை வனவிலங்கு வழித்தடத்தை மறித்து கட்டப்பட்ட விடுதி ஆக்கிரமிப்புகளை அகற்ற உயர்நீதிமன்றம் உத்தரவிட்டுள்ளது.",
        "category": "Forest Encroachment",
        "district": "Theni & Megamalai",
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State/megamalai-corridor-encroachment-eviction",
        "species": ["Elephant"],
        "time": datetime.combine(older_date, datetime.min.time()).replace(hour=10, minute=0),
        "date_status": "OLD"
    }
]

db_storage.articles.clear()

for art in status_articles:
    db_storage.articles[art["id"]] = Article(
        id=art["id"],
        title_en=art["title_en"],
        title_ta=art["title_ta"],
        content_en=art["content_en"],
        content_ta=art["content_ta"],
        summary_en=f"• {art['content_en']}",
        summary_ta=f"• {art['content_ta']}",
        category=art["category"],
        conflict_level="High" if "Crime" in art["category"] or "Conflict" in art["category"] else "Medium",
        district=art["district"],
        species=art["species"],
        source_name=art["source"],
        source_url=art["url"],
        published_at=art["time"],
        tags=[art["category"], art["district"]] + art["species"],
        key_entities=KeyEntities(
            locations=[art["district"]],
            species=art["species"],
            authorities=["Tamil Nadu Forest Department", "TNFWCCB"],
            impact="Date Status Pipeline Categorization"
        ),
        sentiment="Neutral",
        date_status=art["date_status"],
        created_at=art["time"]
    )

db_storage.save_data()
print(f"Seeded date_status articles successfully! ({len(db_storage.articles)} total)")
