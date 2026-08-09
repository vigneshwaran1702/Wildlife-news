import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage
from app.models.schemas import Article, KeyEntities

now = datetime.now()

official_articles = [
    {
        "id": "tn_official_001",
        "title_en": "Environmentalists flag land use changes in Periya-Pakranthalam elephant corridor",
        "title_ta": "பெரியா-பக்ராந்தளம் யானை வழித்தட நில பயன்பாட்டு மாற்றங்கள் குறித்து சுற்றுச்சூழல் ஆர்வலர்கள் கவலை",
        "content_en": "Environmentalists and the ANEC Trust submitted a representation to senior forest department officials seeking immediate intervention to protect the Periya Pakranthalam elephant corridor. They flagged ongoing excavation and construction on private land bordering reserve forests that obstruct elephant movement between Aralam, Kottiyur, and Mudumalai landscapes.",
        "content_ta": "பெரியா பக்ராந்தளம் யானை வழித்தடத்தைப் பாதுகாக்க உடனடி தலையீடு கோரி மூத்த வனத்துறை அதிகாரிகளிடம் சுற்றுச்சூழல் ஆர்வலர்கள் மனு அளித்தனர். அரளம், கொட்டியூர் மற்றும் முதுமலை இடையே யானைகள் நகர்வதைத் தடுக்கும் தனியார் நில ஆக்கிரமிப்புகளை அவர்கள் சுட்டிக்காட்டினர்.",
        "category": "Corridor Protection",
        "district": "Nilgiris / Interstate Corridor",
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/kerala/article71317230.ece",
        "species": ["Elephant"],
        "time": now.replace(hour=11, minute=13)
    },
    {
        "id": "tn_official_002",
        "title_en": "Thousands of forest dwellers protest in Theni, seek TN's intervention on FRA rights before Supreme Court",
        "title_ta": "தேனியில் ஆயிரக்கணக்கான வனவாசிகள் போராட்டம்: உச்சநீதிமன்றத்தில் வன உரிமைச் சட்டத்தை வலியுறுத்தக் கோரிக்கை",
        "content_en": "Urging the Tamil Nadu government to safeguard legal rights guaranteed under the Forest Rights Act (FRA), 2006, before the Supreme Court, thousands of traditional forest dwellers from 98 villages across Megamalai and Varusanadu staged a demonstration at the Theni Collectorate, emphasizing Gram Sabha authority in verifying land claims.",
        "content_ta": "வன உரிமைச் சட்டம் 2006ன் கீழ் உத்திரவாதம் அளிக்கப்பட்ட சட்டப்பூர்வ உரிமைகளைப் பாதுகாக்கக் கோரி, மேகமலை மற்றும் வருசநாடு பகுதிகளைச் சேர்ந்த ஆயிரக்கணக்கான வனவாசிகள் தேனி ஆட்சியர் அலுவலகம் முன் ஆர்ப்பாட்டம் நடத்தினர்.",
        "category": "Forest Rights (FRA)",
        "district": "Theni / Megamalai Range",
        "source": "DT Next",
        "url": "https://www.dtnext.in/news/tamilnadu/thousands-of-forest-dwellers-protest-in-theni",
        "species": ["Forest Dwellers"],
        "time": now.replace(hour=12, minute=30)
    },
    {
        "id": "tn_official_003",
        "title_en": "Official inquiry committee formed into illegal felling of 200 trees in Kundha forest, Nilgiris",
        "title_ta": "நீலகிரி குந்தா வனப்பகுதியில் 200 மரங்கள் சட்டவிரோதமாக வெட்டப்பட்ட வழக்கில் விசாரணைக் குழு அமைப்பு",
        "content_en": "An official inquiry committee was constituted to investigate the illegal felling of over 200 mature trees in the Kundha Reserve Forest area. Field inspections were ordered to fix accountability among timber contractors and assess forest boundary encroachments.",
        "content_ta": "குந்தா காப்புக்காடு பகுதியில் 200க்கும் மேற்பட்ட மரங்கள் சட்டவிரோதமாக வெட்டப்பட்டது தொடர்பாக விசாரிக்க அதிகாரப்பூர்வ விசாரணைக் குழு அமைக்கப்பட்டது. மரம் வெட்டுபவர்கள் மீது நடவடிக்கை எடுக்க உத்தரவிடப்பட்டுள்ளது.",
        "category": "Forest Crime",
        "district": "Nilgiris / Kundha Range",
        "source": "Dinakaran (தினகரன்)",
        "url": "https://www.dinakaran.com/state-news/",
        "species": ["Teak", "Rosewood"],
        "time": now.replace(hour=13, minute=45)
    },
    {
        "id": "tn_official_004",
        "title_en": "Intensive night patrolling and solar fencing work fast-tracked in Tenkasi and Tirunelveli forest border villages",
        "title_ta": "தென்காசி, திருநெல்வேலி வனப்பகுதி கிராமங்களில் இரவு நேர ரோந்து மற்றும் சோலார் வேலி பணிகள் தீவிரமாக்கம்",
        "content_en": "Following wild boar and sloth bear movements into agricultural fields along the Sivagiri-Kadayam Western Ghats belt, special night-patrolling squads with searchlights were deployed and hanging solar electric fence work was fast-tracked by the Forest Department.",
        "content_ta": "சிவகாசி-கடையம் மேற்குத் தொடர்ச்சி மலைப் பகுதியில் காட்டுப்பன்றி மற்றும் கரடிகள் விளைநிலங்களுக்குள் நுழைவதைத் தடுக்க, சிறப்பு இரவு ரோந்துப் படைகள் அமைக்கப்பட்டு சோலார் மின் வேலி அமைக்கும் பணி முடுக்கிவிடப்பட்டுள்ளது.",
        "category": "Conflict Mitigation",
        "district": "Tirunelveli & Tenkasi",
        "source": "Dinamani (தினமணி)",
        "url": "https://www.dinamani.com/all-editions",
        "species": ["Wild Boar", "Sloth Bear"],
        "time": now.replace(hour=14, minute=50)
    },
    {
        "id": "tn_official_005",
        "title_en": "Special anti-poaching and timber smuggling checkpoints reinforced along Yercaud ghat roads",
        "title_ta": "ஏற்காடு மலைப்பாதையில் வேட்டைத் தடுப்பு மற்றும் மரக் கடத்தல் தடுப்புச் சோதனைச் சாவடிகள் பலப்படுத்தல்",
        "content_en": "Salem Forest Division intensified vehicle checking and deployed mobile anti-poaching squads along the Yercaud 20-hairpin bend road and surrounding reserve forest limits to check illegal tree felling, wildlife disturbance, and unauthorized night camping.",
        "content_ta": "சேலம் வனக்கோட்டம் ஏற்காடு 20 கொண்டைஊசி வளைவு பாதையில் சட்டவிரோத மரம் வெட்டுதல் மற்றும் வனவிலங்கு தொந்தரவுகளைத் தடுக்க வேட்டைத் தடுப்புச் சோதனைச் சாவடிகளைப் பலப்படுத்தியுள்ளது.",
        "category": "Protection Patrol",
        "district": "Salem / Yercaud Division",
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State",
        "species": ["Leopard", "Sandalwood"],
        "time": now.replace(hour=15, minute=40)
    },
    {
        "id": "tn_official_006",
        "title_en": "Tamil Nadu Forest Department employees demand resolution of pay anomalies for forest watchers and guards",
        "title_ta": "வனக்காவலர்கள் ஊதிய முரண்பாடுகளை களைய வலியுறுத்தி தமிழ்நாடு வனத்துறை ஊழியர்கள் கோரிக்கை",
        "content_en": "Forest Watchers and Guards Associations submitted representations regarding long-standing pay parity issues with Grade-I police constables and requested a transparent, computerized counseling system for field staff transfers across forest circles.",
        "content_ta": "வனக்காவலர்கள் மற்றும் வனக் காவலர் சங்கத்தினர் தங்களது நீண்டகால ஊதிய முரண்பாடுகளை களையக் கோரியும், வெளிப்படையான மாறுதல் கலந்தாய்வு முறையை அமல்படுத்தக் கோரியும் வனத்துறை தலைவரிடம் மனு அளித்தனர்.",
        "category": "Staff Welfare",
        "district": "Statewide / Staff Welfare",
        "source": "The New Indian Express",
        "url": "https://www.newindianexpress.com/states/tamil-nadu",
        "species": ["Staff Welfare"],
        "time": now.replace(hour=16, minute=15)
    },
    {
        "id": "tn_official_007",
        "title_en": "Man arrested for chasing wild elephant on Aliyar–Valparai road near Samamatta canal",
        "title_ta": "ஆழியாறு - வால்பாறை சாலையில் காட்டு யானையை விரட்டிய நபர் கைது: ஆனைமலை புலிகள் காப்பகம் நடவடிக்கை",
        "content_en": "Anamalai Tiger Reserve (ATR) forest officials arrested K. Mayavan (48) of Chinnarpathy settlement for chasing a wild elephant along the Aliyar–Valparai road. Following viral video evidence, the suspect was booked under the Wildlife Protection Act and remanded to judicial custody.",
        "content_ta": "ஆழியாறு-வால்பாறை சாலையில் காட்டு யானையை விரட்டிச் சென்ற சின்னார்பதி குடியிருப்பைச் சேர்ந்த மாயவன் (48) என்பவரை ஆனைமலை புலிகள் காப்பக வனத்துறையினர் கைது செய்து வனவிலங்கு பாதுகாப்புச் சட்டத்தில் சிறையில் அடைத்தனர்.",
        "category": "Wildlife Offense",
        "district": "Coimbatore / ATR Pollachi",
        "source": "Times of India",
        "url": "https://timesofindia.indiatimes.com/city/coimbatore/articleshow/133051069.cms",
        "species": ["Elephant"],
        "time": now.replace(hour=16, minute=28)
    }
]

db_storage.articles.clear()

for art in official_articles:
    db_storage.articles[art["id"]] = Article(
        id=art["id"],
        title_en=art["title_en"],
        title_ta=art["title_ta"],
        content_en=art["content_en"],
        content_ta=art["content_ta"],
        summary_en=f"• {art['content_en']}",
        summary_ta=f"• {art['content_ta']}",
        category=art["category"],
        conflict_level="High" if "Offense" in art["category"] or "Crime" in art["category"] else "Medium",
        district=art["district"],
        species=art["species"],
        source_name=art["source"],
        source_url=art["url"],
        published_at=art["time"],
        tags=[art["category"], art["district"]] + art["species"],
        key_entities=KeyEntities(
            locations=[art["district"]],
            species=art["species"],
            authorities=["Tamil Nadu Forest Department"],
            impact="Official Evening Scan Bulletin"
        ),
        sentiment="Neutral",
        created_at=art["time"]
    )

db_storage.save_data()
print(f"Successfully seeded official Tamil Nadu Forest Department bulletin data ({len(db_storage.articles)} articles)")
