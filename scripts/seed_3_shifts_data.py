import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage
from app.models.schemas import Article, KeyEntities

today = datetime.now().date()

shift_articles = [
    # SHIFT 1: 08:00 AM - 05:00 PM
    {
        "id": "shift1_001",
        "title_en": "Environmentalists flag land use changes in Periya-Pakranthalam elephant corridor",
        "title_ta": "பெரியா-பக்ராந்தளம் யானை வழித்தட நில பயன்பாட்டு மாற்றங்கள் குறித்து சுற்றுச்சூழல் ஆர்வலர்கள் கவலை",
        "content_en": "Environmentalists and the ANEC Trust submitted a representation seeking immediate protection of the Periya Pakranthalam elephant corridor.",
        "content_ta": "பெரியா பக்ராந்தளம் யானை வழித்தடத்தைப் பாதுகாக்க உடனடி தலையீடு கோரி மூத்த வனத்துறை அதிகாரிகளிடம் சுற்றுச்சூழல் ஆர்வலர்கள் மனு அளித்தனர்.",
        "category": "Corridor Protection",
        "district": "Nilgiris / Interstate Corridor",
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/kerala/article71317230.ece",
        "species": ["Elephant"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=11, minute=13)
    },
    {
        "id": "shift1_002",
        "title_en": "Thousands of forest dwellers protest in Theni, seek TN's intervention on FRA rights before Supreme Court",
        "title_ta": "தேனியில் ஆயிரக்கணக்கான வனவாசிகள் போராட்டம்: உச்சநீதிமன்றத்தில் வன உரிமைச் சட்டத்தை வலியுறுத்தக் கோரிக்கை",
        "content_en": "Traditional forest dwellers from 98 villages across Megamalai staged a demonstration at Theni Collectorate.",
        "content_ta": "வன உரிமைச் சட்டம் 2006ன் கீழ் உத்திரவாதம் அளிக்கப்பட்ட சட்டப்பூர்வ உரிமைகளைப் பாதுகாக்கக் கோரி வனவாசிகள் போராட்டம் நடத்தினர்.",
        "category": "Forest Rights (FRA)",
        "district": "Theni / Megamalai Range",
        "source": "DT Next",
        "url": "https://www.dtnext.in/news/tamilnadu/thousands-of-forest-dwellers-protest-in-theni",
        "species": ["Forest Dwellers"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=12, minute=30)
    },
    {
        "id": "shift1_003",
        "title_en": "Official inquiry committee formed into illegal felling of 200 trees in Kundha forest, Nilgiris",
        "title_ta": "நீலகிரி குந்தா வனப்பகுதியில் 200 மரங்கள் சட்டவிரோதமாக வெட்டப்பட்ட வழக்கில் விசாரணைக் குழு அமைப்பு",
        "content_en": "An inquiry committee was constituted to investigate illegal felling of 200 mature trees in Kundha Reserve Forest.",
        "content_ta": "குந்தா காப்புக்காடு பகுதியில் 200க்கும் மேற்பட்ட மரங்கள் வெட்டப்பட்டது தொடர்பாக விசாரிக்க விசாரணைக் குழு அமைக்கப்பட்டது.",
        "category": "Forest Crime",
        "district": "Nilgiris / Kundha Range",
        "source": "Dinakaran (தினகரன்)",
        "url": "https://www.dinakaran.com/state-news/kundha-forest-tree-felling-case",
        "species": ["Teak"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=13, minute=45)
    },
    {
        "id": "shift1_004",
        "title_en": "Intensive night patrolling and solar fencing work fast-tracked in Tenkasi and Tirunelveli forest border villages",
        "title_ta": "தென்காசி, திருநெல்வேலி வனப்பகுதி கிராமங்களில் இரவு நேர ரோந்து மற்றும் சோலார் வேலி பணிகள் தீவிரமாக்கம்",
        "content_en": "Night-patrolling squads were deployed and solar electric fencing work fast-tracked along Western Ghats belt.",
        "content_ta": "மேற்குத் தொடர்ச்சி மலைப் பகுதியில் சிறப்பு இரவு ரோந்துப் படைகள் அமைக்கப்பட்டு சோலார் வேலி பணி முடுக்கிவிடப்பட்டுள்ளது.",
        "category": "Conflict Mitigation",
        "district": "Tirunelveli & Tenkasi",
        "source": "Dinamani (தினமணி)",
        "url": "https://www.dinamani.com/all-editions/tirunelveli-tenkasi-forest-solar-fencing",
        "species": ["Wild Boar", "Sloth Bear"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=14, minute=50)
    },
    {
        "id": "shift1_005",
        "title_en": "Special anti-poaching and timber smuggling checkpoints reinforced along Yercaud ghat roads",
        "title_ta": "ஏற்காடு மலைப்பாதையில் வேட்டைத் தடுப்பு மற்றும் மரக் கடத்தல் தடுப்புச் சோதனைச் சாவடிகள் பலப்படுத்தல்",
        "content_en": "Salem Forest Division reinforced anti-poaching checkpoints along Yercaud 20-hairpin bend ghat road.",
        "content_ta": "சேலம் வனக்கோட்டம் ஏற்காடு 20 கொண்டைஊசி வளைவு பாதையில் வேட்டைத் தடுப்புச் சோதனைச் சாவடிகளைப் பலப்படுத்தியுள்ளது.",
        "category": "Protection Patrol",
        "district": "Salem / Yercaud Division",
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State/yercaud-anti-poaching-checkpoints",
        "species": ["Sandalwood"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=15, minute=40)
    },
    {
        "id": "shift1_006",
        "title_en": "Tamil Nadu Forest Department employees demand resolution of pay anomalies for forest watchers and guards",
        "title_ta": "வனக்காவலர்கள் ஊதிய முரண்பாடுகளை களைய வலியுறுத்தி தமிழ்நாடு வனத்துறை ஊழியர்கள் கோரிக்கை",
        "content_en": "Forest Watchers Associations submitted representations regarding pay parity issues.",
        "content_ta": "வனக்காவலர்கள் ஊதிய முரண்பாடுகளை களையக் கோரி வனத்துறை தலைவரிடம் மனு அளித்தனர்.",
        "category": "Staff Welfare",
        "district": "Statewide / Staff Welfare",
        "source": "The New Indian Express",
        "url": "https://www.newindianexpress.com/states/tamil-nadu/tn-forest-guards-pay-parity-demand",
        "species": ["Staff Welfare"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=16, minute=15)
    },
    {
        "id": "shift1_007",
        "title_en": "Man arrested for chasing wild elephant on Aliyar–Valparai road near Samamatta canal",
        "title_ta": "ஆழியாறு - வால்பாறை சாலையில் காட்டு யானையை விரட்டிய நபர் கைது: ஆனைமலை புலிகள் காப்பகம் நடவடிக்கை",
        "content_en": "ATR forest officials arrested a man for chasing a wild elephant along Aliyar–Valparai road.",
        "content_ta": "ஆழியாறு-வால்பாறை சாலையில் காட்டு யானையை விரட்டிச் சென்ற நபர் கைது செய்யப்பட்டு சிறையில் அடைக்கப்பட்டார்.",
        "category": "Wildlife Offense",
        "district": "Coimbatore / ATR Pollachi",
        "source": "Times of India",
        "url": "https://timesofindia.indiatimes.com/city/coimbatore/articleshow/133051069.cms",
        "species": ["Elephant"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=16, minute=28)
    },

    # SHIFT 2: 05:00 PM - 09:00 PM
    {
        "id": "shift2_001",
        "title_en": "Mudumalai Tiger Reserve deploys thermal drones to monitor wild elephant herd near Masinagudi",
        "title_ta": "மசினகுடி அருகே காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பகம் வெப்ப ட்ரோன்களை இயக்கியது",
        "content_en": "Forest officials in Mudumalai activated thermal imaging drones to track a herd of 14 wild elephants near Masinagudi.",
        "content_ta": "மசினகுடி அருகே நகரும் 14 காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பகம் வெப்ப ட்ரோன்களை இயக்கியது.",
        "category": "Human-Wildlife Conflict",
        "district": "Nilgiris / Masinagudi",
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/tamil-nadu/mudumalai-thermal-drones-elephant-monitoring/article883920.ece",
        "species": ["Elephant"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=17, minute=45)
    },
    {
        "id": "shift2_002",
        "title_en": "TN Forest Department establishes 24x7 Wildlife Crime Control Unit in Sathyamangalam Tiger Reserve",
        "title_ta": "சத்தியமங்கலம் புலிகள் காப்பகத்தில் 24 மணி நேர வனக்குற்ற கட்டுப்பாட்டு மையத்தை அமைத்தது தமிழ்நாடு வனத்துறை",
        "content_en": "To prevent poaching and illegal timber trafficking, STR set up a 24x7 control room with vehicle scanners.",
        "content_ta": "வேட்டையாடுதல் மற்றும் மரக் கடத்தலைத் தடுக்க சத்தியமங்கலம் புலிகள் காப்பகத்தில் 24 மணி நேர கட்டுப்பாட்டு அறை அமைக்கப்பட்டது.",
        "category": "Wildlife Crime & Rescue",
        "district": "Erode & Sathyamangalam",
        "source": "The New Indian Express",
        "url": "https://www.newindianexpress.com/states/tamil-nadu/str-wildlife-crime-control-unit-24x7",
        "species": ["Tiger", "Elephant"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=18, minute=30)
    },
    {
        "id": "shift2_003",
        "title_en": "Anamalai Tiger Reserve opens new eco-tourism bamboo rafting route in Topslip Pollachi",
        "title_ta": "பொள்ளாச்சி டாப்சிலிப்பில் புதிய மூங்கில் படகு சவாரி சூழல் சுற்றூலாவை தொடங்கியது ஆனைமலை புலிகள் காப்பகம்",
        "content_en": "ATR management inaugurated an eco-friendly bamboo rafting safari along Karianshola canopy waterways.",
        "content_ta": "இயற்கை சுற்றுலா பயணிகளுக்காக டாப்சிலிப் கரியான்சோலா நீர்வழிகளில் மூங்கில் படகு சவாரி தொடங்கப்பட்டது.",
        "category": "Eco-Tourism & Sanctuaries",
        "district": "Tiruppur & Anamalai",
        "source": "DT Next",
        "url": "https://www.dtnext.in/news/tamilnadu/anamalai-topslip-bamboo-rafting-ecotourism",
        "species": ["Gaur"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=19, minute=15)
    },
    {
        "id": "shift2_004",
        "title_en": "Forest Department Constructs 80 km Green Firebreaks across Kodaikanal Pine Forests",
        "title_ta": "கொடைக்கானல் பைன் காடுகளில் 80 கி.மீ பச்சை தீத்தடுப்பு கோடுகளை உருவாக்கியது வனத்துறை",
        "content_en": "Dindigul Forest Division completed 80 km of green firebreaks in Kodaikanal sanctuary slopes.",
        "content_ta": "திண்டுக்கல் வனக்கோட்டம் கொடைக்கானல் சரிவுகளில் காட்டுத் தீயைத் தடுக்க 80 கி.மீ பச்சை தீத்தடுப்பு கோடுகளை உருவாக்கியுள்ளது.",
        "category": "Forest Fire & Safety",
        "district": "Dindigul & Kodaikanal",
        "source": "Dinamani (தினமணி)",
        "url": "https://www.dinamani.com/all-editions/kodaikanal-green-firebreaks-forest",
        "species": ["Pine Forest"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=20, minute=20)
    },

    # SHIFT 3: 09:00 PM - 08:00 AM
    {
        "id": "shift3_001",
        "title_en": "Madras High Court orders strict eviction of resort encroachments in Megamalai elephant corridor",
        "title_ta": "மேகமலை யானை வழித்தட விடுதி ஆக்கிரமிப்புகளை உடனடியாக அகற்ற சென்னை உயர்நீதிமன்றம் உத்தரவு",
        "content_en": "The High Court directed Theni administration to clear commercial resort encroachments obstructing Megamalai corridor.",
        "content_ta": "மேகமலை-பெரியார் வனவிலங்கு வழித்தடத்தை மறித்து கட்டப்பட்ட விடுதி ஆக்கிரமிப்புகளை அகற்ற உயர்நீதிமன்றம் உத்தரவிட்டது.",
        "category": "Forest Encroachment",
        "district": "Theni & Megamalai",
        "source": "Dina Thanthi (தினத்தந்தி)",
        "url": "https://www.dailythanthi.com/News/State/megamalai-corridor-encroachment-eviction",
        "species": ["Elephant"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=21, minute=30)
    },
    {
        "id": "shift3_002",
        "title_en": "Kalakad Mundanthurai Reserve anti-poaching team rescues injured female sloth bear in Papanasam",
        "title_ta": "பாபநாசத்தில் காயமடைந்த பெண் கரடியை பத்திரமாக மீட்ட களக்காடு முண்டந்துறை வேட்டைத்தடுப்புப் படை",
        "content_en": "KMTR veterinary doctors treated a female sloth bear injured in a snare trap near Papanasam.",
        "content_ta": "பாபநாசம் வனச்சரகத்தில் கண்ணியில் சிக்கி காயமடைந்த பெண் கரடிக்கு சிகிச்சை அளித்து மீட்டனர்.",
        "category": "Wildlife Crime & Rescue",
        "district": "Tirunelveli & KMTR",
        "source": "Dinamalar (தினமலர்)",
        "url": "https://www.dinamalar.com/news_detail.asp?id=kmtr-sloth-bear-rescue-papanasam",
        "species": ["Sloth Bear"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=22, minute=15)
    },
    {
        "id": "shift3_003",
        "title_en": "Vedanthangal Waterbird Sanctuary welcomes 30,000 seasonal migratory birds in Chengalpattu",
        "title_ta": "செங்கல்பட்டு வேடந்தாங்கல் சரணாலயத்திற்கு 30,000 பருவமழை கால புலம்பெயர் பறவைகள் வருகை",
        "content_en": "Over 30,000 nesting migratory waterbirds arrived at Vedanthangal Waterbird Sanctuary.",
        "content_ta": "வேடந்தாங்கல் பறவைகள் சரணாலயத்தில் 30,000க்கும் மேற்பட்ட புலம்பெயர் பறவைகள் கூடு கட்டி வருகின்றன.",
        "category": "Species Conservation",
        "district": "Chengalpattu & Vedanthangal",
        "source": "Hindu Tamil Thisai (தமிழ் இந்து)",
        "url": "https://www.hindutamil.in/news/environment/vedanthangal-migratory-birds-season",
        "species": ["Migratory Birds"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=23, minute=45)
    },
    {
        "id": "shift3_004",
        "title_en": "Gulf of Mannar Marine National Park deploys patrol speedboats against sea turtle poaching in Ramanathapuram",
        "title_ta": "இராமநாதபுரத்தில் கடல் ஆமைகள் வேட்டையைத் தடுக்க ரோந்து அதிவேக படகுகளை இறக்கியது மன்னார் வளைகுடா பூங்கா",
        "content_en": "Marine forest rangers launched speed patrol boats along Gulf of Mannar islands to prevent turtle poaching.",
        "content_ta": "மன்னார் வளைகுடா தீவுகளில் கடல் ஆமைகள் வேட்டையாடப்படுவதைத் தடுக்க அதிவேக படகுகளை இயக்கத் தொடங்கினர்.",
        "category": "Wildlife Crime & Rescue",
        "district": "Ramanathapuram & Gulf of Mannar",
        "source": "Times of India",
        "url": "https://timesofindia.indiatimes.com/city/madurai/gulf-of-mannar-sea-turtle-patrol",
        "species": ["Sea Turtle"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=6, minute=15)
    },
    {
        "id": "shift3_005",
        "title_en": "Point Calimere Wildlife Sanctuary inaugurates Blackbuck Eco-Watchtower in Nagapattinam",
        "title_ta": "நாகப்பட்டினம் கோடியக்கரை சரணாலயத்தில் வெளிமான் கண்காணிப்பு கோபுரத்தை திறந்து வைத்தது வனத்துறை",
        "content_en": "Nagapattinam forest division opened an eco-watchtower at Point Calimere Sanctuary for blackbuck observation.",
        "content_ta": "கோடியக்கரை வனவிலங்கு சரணாலயத்தில் வெளிமான்களைப் பார்க்க சூழல் கண்காணிப்பு கோபுரத்தை திறந்தனர்.",
        "category": "Eco-Tourism & Sanctuaries",
        "district": "Nagapattinam & Point Calimere",
        "source": "Puthiya Thalaimurai (புதிய தலைமுறை)",
        "url": "https://www.puthiyathalaimurai.com/news/tamilnadu/point-calimere-blackbuck-watchtower",
        "species": ["Blackbuck"],
        "time": datetime.combine(today, datetime.min.time()).replace(hour=7, minute=30)
    }
]

db_storage.articles.clear()

for art in shift_articles:
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
            impact="3-Shift Scheduled Media Scan"
        ),
        sentiment="Neutral",
        created_at=art["time"]
    )

db_storage.save_data()
print(f"Successfully seeded articles into 3 distinct shift time windows ({len(db_storage.articles)} articles total)")
