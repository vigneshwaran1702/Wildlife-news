import sys
import os
import urllib.parse
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.services.storage import db_storage
from app.models.schemas import Article, KeyEntities

now = datetime.now()

fresh_today_articles = [
    {
        'id': 'today_001',
        'title_en': 'Mudumalai Tiger Reserve deploys thermal drones to monitor wild elephant herd near Masinagudi',
        'title_ta': 'மசினகுடி அருகே காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பகம் வெப்ப ட்ரோன்களை இயக்கியது',
        'content_en': 'Forest officials in Mudumalai Tiger Reserve have activated high-resolution thermal imaging drones to track a herd of 14 wild elephants moving close to human settlements in Masinagudi range, Nilgiris.',
        'content_ta': 'நீலகிரி மாவட்டம் மசினகுடி அருகே மனித குடியிருப்புகளுக்கு அருகில் நகரும் 14 காட்டு யானைக் கூட்டத்தை கண்காணிக்க முதுமலை புலிகள் காப்பக வனத்துறையினர் உயர் வெப்ப இமேஜிங் ட்ரோன்களை இயக்கியுள்ளனர்.',
        'category': 'Human-Wildlife Conflict',
        'district': 'Nilgiris',
        'species': ['Elephant'],
        'source': 'The Hindu'
    },
    {
        'id': 'today_002',
        'title_en': 'TN Forest Department establishes 24x7 Wildlife Crime Control Unit in Sathyamangalam Tiger Reserve',
        'title_ta': 'சத்தியமங்கலம் புலிகள் காப்பகத்தில் 24 மணி நேர வனக்குற்ற கட்டுப்பாட்டு மையத்தை அமைத்தது தமிழ்நாடு வனத்துறை',
        'content_en': 'To prevent poaching and illegal timber trafficking along the interstate border, Sathyamangalam Tiger Reserve authorities set up a dedicated 24x7 control room with vehicle scanning checkpoints.',
        'content_ta': 'மாநில எல்லைப் பகுதியில் வேட்டையாடுதல் மற்றும் சட்டவிரோத மரக் கடத்தலைத் தடுக்க, சத்தியமங்கலம் புலிகள் காப்பக வனத்துறையினர் வாகன ஸ்கேனிங் சோதனைச் சாவடிகளுடன் 24 மணி நேர கட்டுப்பாட்டு அறையை அமைத்துள்ளனர்.',
        'category': 'Wildlife Crime & Rescue',
        'district': 'Erode & Sathyamangalam',
        'species': ['Tiger', 'Elephant'],
        'source': 'The New Indian Express'
    },
    {
        'id': 'today_003',
        'title_en': 'Anamalai Tiger Reserve opens new eco-tourism bamboo rafting route in Topslip Pollachi',
        'title_ta': 'பொள்ளாச்சி டாப்சிலிப்பில் புதிய மூங்கில் படகு சவாரி சூழல் சுற்றுலா வைத்த தொடங்கியது ஆனைமலை புலிகள் காப்பகம்',
        'content_en': 'Anamalai Tiger Reserve management has inaugurated an eco-friendly bamboo rafting safari along the Karianshola canopy waterways in Topslip for nature tourists and wildlife enthusiasts.',
        'content_ta': 'இயற்கை சுற்றுலா பயணிகள் மற்றும் வனவிலங்கு ஆர்வலர்களுக்காக ஆனைமலை புலிகள் காப்பகம் டாப்சிலிப் கரியான்சோலா நீர்வழிகளில் சூழல் நட்பு மூங்கில் படகு சவாரியை அறிமுகப்படுத்தியுள்ளது.',
        'category': 'Eco-Tourism & Sanctuaries',
        'district': 'Tiruppur & Anamalai',
        'species': ['Gaur (Indian Bison)', 'Lion-tailed Macaque'],
        'source': 'DT Next'
    },
    {
        'id': 'today_004',
        'title_en': 'Forest Department Constructs 80 km Green Firebreaks across Kodaikanal Pine Forests',
        'title_ta': 'கொடைக்கானல் பைன் காடுகளில் 80 கி.மீ பச்சை தீத்தடுப்பு கோடுகளை உருவாக்கியது வனத்துறை',
        'content_en': 'In response to high temperatures, Dindigul Forest Division completed 80 km of green firebreaks and moisture retaining trenches in Kodaikanal sanctuary slopes to prevent forest blazes.',
        'content_ta': 'அதிக வெப்பநிலையைக் கருத்தில் கொண்டு, திண்டுக்கல் வனக்கோட்டம் கொடைக்கானல் சரணாலய சரிவுகளில் காட்டுத் தீயைத் தடுக்க 80 கி.மீ பச்சை தீத்தடுப்பு கோடுகளை உருவாக்கியுள்ளது.',
        'category': 'Forest Fire & Safety',
        'district': 'Dindigul & Kodaikanal',
        'species': ['Forest Ecosystem'],
        'source': 'Dinamani (தினமணி)'
    },
    {
        'id': 'today_005',
        'title_en': 'Madras High Court orders strict eviction of resort encroachments in Megamalai elephant corridor',
        'title_ta': 'மேகமலை யானை வழித்தட விடுதி ஆக்கிரமிப்புகளை உடனடியாக அகற்ற சென்னை உயர்நீதிமன்றம் உத்தரவு',
        'content_en': 'The Madras High Court bench directed Theni district administration and Forest Department to clear 12 commercial resort encroachments obstructing the Megamalai-Periyar wildlife migration corridor.',
        'content_ta': 'மேகமலை-பெரியார் வனவிலங்கு இடப்பெயர்வு வழித்தடத்தை மறித்து கட்டப்பட்ட 12 வணிக விடுதி ஆக்கிரமிப்புகளை அகற்ற தேனி மாவட்ட நிர்வாகம் மற்றும் வனத்துறைக்கு சென்னை உயர்நீதிமன்றம் உத்தரவிட்டுள்ளது.',
        'category': 'Forest Encroachment',
        'district': 'Theni & Megamalai',
        'species': ['Elephant', 'Leopard'],
        'source': 'Dina Thanthi (தினத்தந்தி)'
    },
    {
        'id': 'today_006',
        'title_en': 'Kalakad Mundanthurai Reserve anti-poaching team rescues injured female sloth bear in Papanasam',
        'title_ta': 'பாபநாசத்தில் காயமடைந்த பெண் கரடியை பத்திரமாக மீட்ட களக்காடு முண்டந்துறை வேட்டைத்தடுப்புப் படை',
        'content_en': 'Forest veterinary doctors at KMTR successfully tranquilized and treated a four-year-old female sloth bear injured in a snare trap near Papanasam forest range in Tirunelveli district.',
        'content_ta': 'திருநெல்வேலி மாவட்டம் பாபநாசம் வனச்சரகத்தில் கண்ணியில் சிக்கி காயமடைந்த 4 வயது பெண் கரடிக்கு களக்காடு முண்டந்துறை வனநடை மருத்துவக் குழுவினர் சிகிச்சை அளித்து மீட்டுள்ளனர்.',
        'category': 'Wildlife Crime & Rescue',
        'district': 'Tirunelveli & KMTR',
        'species': ['Sloth Bear'],
        'source': 'Dinamalar (தினமலர்)'
    },
    {
        'id': 'today_007',
        'title_en': 'Vedanthangal Waterbird Sanctuary welcomes 30,000 seasonal migratory birds in Chengalpattu',
        'title_ta': 'செங்கல்பட்டு வேடந்தாங்கல் சரணாலயத்திற்கு 30,000 பருவமழை கால புலம்பெயர் பறவைகள் வருகை',
        'content_en': 'With abundant monsoon water storage, Chengalpattu forest division reported the arrival of over 30,000 nesting migratory waterbirds including openbill storks and spot-billed pelicans at Vedanthangal.',
        'content_ta': 'செங்கல்பட்டு மாவட்டம் வேடந்தாங்கல் பறவைகள் சரணாலயத்தில் திறந்தவாக்கு நாரைகள் மற்றும் கூழைக்கடாக்கள் உள்ளிட்ட 30,000க்கும் மேற்பட்ட பறவைகள் கூடு கட்டி இனப்பெருக்கம் செய்து வருகின்றன.',
        'category': 'Species Conservation',
        'district': 'Chengalpattu & Vedanthangal',
        'species': ['Migratory Birds'],
        'source': 'Hindu Tamil Thisai (தமிழ் இந்து)'
    },
    {
        'id': 'today_008',
        'title_en': 'Gulf of Mannar Marine National Park deploys patrol speedboats against sea turtle poaching in Ramanathapuram',
        'title_ta': 'இராமநாதபுரத்தில் கடல் ஆமைகள் வேட்டையைத் தடுக்க ரோந்து அதிவேக படகுகளை இறக்கியது மன்னார் வளைகுடா பூங்கா', 'content_en': 'Ramanathapuram marine forest rangers launched high-speed sea patrol boats along Gulf of Mannar islands to intercept illegal poaching of endangered green sea turtles and dugongs.',
        'content_ta': 'இராமநாதபுரம் கடலோர வனத்துறையினர் மன்னார் வளைகுடா தீவுகளில் கடல் ஆமைகள் மற்றும் கடல் பசுக்கள் வேட்டையாடப்படுவதைத் தடுக்க அதிவேக ரோந்து படகுகளை இயக்கத் தொடங்கியுள்ளனர்.',
        'category': 'Wildlife Crime & Rescue',
        'district': 'Ramanathapuram & Gulf of Mannar',
        'species': ['Sea Turtle', 'Dugong'],
        'source': 'Times of India'
    },
    {
        'id': 'today_009',
        'title_en': 'Coimbatore Forest Division sets up 10 AI camera towers along Mettupalayam railway elephant corridor',
        'title_ta': 'மேட்டுப்பாளையம் ரயில்வே யானை வழித்தடத்தில் 10 AI கேமரா கோபுரங்களை அமைத்தது கோவை வனக்கோட்டம்',
        'content_en': 'To eliminate train-elephant collisions on Mettupalayam-Walayar rail track, Coimbatore forest division completed installing AI thermal sensor warning sirens that alert loco pilots 1 km away.',
        'content_ta': 'மேட்டுப்பாளையம்-வாளையாறு ரயில் பாதையில் யானைகள் இரயில் மோதி இறப்பதைத் தடுக்க, 1 கி.மீ தொலைவில் ரயில் ஓட்டுநர்களை எச்சரிக்கும் AI வெப்ப உணர் எச்சரிக்கை கோபுரங்களை கோவை வனத்துறை அமைத்துள்ளது.',
        'category': 'Human-Wildlife Conflict',
        'district': 'Coimbatore',
        'species': ['Elephant'],
        'source': 'News18 Tamil (நியூஸ்18 தமிழ்)'
    },
    {
        'id': 'today_010',
        'title_en': 'Point Calimere Wildlife Sanctuary inaugurates Blackbuck Eco-Watchtower in Nagapattinam',
        'title_ta': 'நாகப்பட்டினம் கோடியக்கரை சரணாலயத்தில் வெளிமான் கண்காணிப்பு கோபுரத்தை திறந்து வைத்தது வனத்துறை',
        'content_en': 'Nagapattinam forest division opened an elevated 40-foot eco-watchtower at Point Calimere Sanctuary allowing tourists to observe wild blackbuck antelopes and flamingos safely.',
        'content_ta': 'நாகப்பட்டினம் மாவட்டம் கோடியக்கரை வனவிலங்கு சரணாலயத்தில் வெளிமான்கள் மற்றும் பூநாரைகளை பாதுகாப்பாகப் பார்க்க 40 அடி உயர சூழல் கண்காணிப்பு கோபுரத்தை வனத்துறை திறந்து வைத்துள்ளது.',
        'category': 'Eco-Tourism & Sanctuaries',
        'district': 'Nagapattinam & Point Calimere',
        'species': ['Blackbuck', 'Flamingo'],
        'source': 'Puthiya Thalaimurai (புதிய தலைமுறை)'
    }
]

db_storage.articles.clear()

for i, d in enumerate(fresh_today_articles):
    q = urllib.parse.quote(f"{d['source']} {d['title_en']} Tamil Nadu")
    art = Article(
        id=d['id'],
        title_en=d['title_en'],
        title_ta=d['title_ta'],
        content_en=d['content_en'],
        content_ta=d['content_ta'],
        summary_en=f"• {d['title_en']}",
        summary_ta=f"• {d['title_ta']}",
        category=d['category'],
        conflict_level='High' if 'Conflict' in d['category'] or 'Crime' in d['category'] else 'Medium',
        district=d['district'],
        species=d['species'],
        source_name=d['source'],
        source_url=f"https://news.google.com/search?q={q}",
        published_at=now - timedelta(minutes=i*20),
        tags=[d['category'], d['district']] + d['species'],
        key_entities=KeyEntities(locations=[d['district']], species=d['species'], authorities=['Tamil Nadu Forest Department'], impact='Active today wildlife protection'),
        sentiment='Positive',
        created_at=now - timedelta(minutes=i*20)
    )
    db_storage.articles[art.id] = art

db_storage.save_data()
print(f"Feed Refreshed! Total 100% TODAY unique articles: {len(db_storage.articles)}")
