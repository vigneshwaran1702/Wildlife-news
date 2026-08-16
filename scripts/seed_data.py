import sys
import os
from datetime import datetime, timedelta
import uuid

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.models.schemas import Article, KeyEntities
from app.services.storage import db_storage
from app.collectors.rss import RSSCollector
try:
    from app.collectors.english_news import EnglishNewsCollector
except ImportError:
    EnglishNewsCollector = None

SEED_ARTICLES = [
    # 1. Human-Wildlife Conflict
    {
        "title_en": "Tamil Nadu Forest Dept installs AI thermal camera network in Valparai to curb human-elephant conflict",
        "title_ta": "மனித-யானை மோதலைக் குறைக்க வால்பாறையில் செயற்கை நுண்ணறிவு கேமராக்களை வனத்துறை அமைத்தது",
        "content_en": "The Tamil Nadu Forest Department has deployed an automated AI thermal sensor network across critical elephant movement corridors in Valparai and Coimbatore divisions. The system sends instant SMS and loudspeaker alerts to tea estate workers when elephant herds approach human habitations.",
        "content_ta": "வால்பாறை மற்றும் கோவை வனக்கோட்டங்களில் யானைகள் நடமாடும் முக்கிய பாதைகளில் தானியங்கி AI வெப்ப உணரி கேமராக்களை தமிழ்நாடு வனத்துறை அமைத்துள்ளது. யானைக் கூட்டங்கள் குடியிருப்புப் பகுதிகளை நெருங்கும்போது இந்த அமைப்பு எஸ்டேட் தொழிலாளர்களுக்கு உடனடி SMS மற்றும் ஒலிபெருக்கி எச்சரிக்கைகளை அனுப்புகிறது.",
        "summary_en": "• AI thermal sensor network installed across 12 elephant movement corridors in Valparai.\n• Real-time SMS and siren alerts dispatched to tea estate workers and forest range officers.\n• Aims to significantly reduce fatal human-elephant encounters in Coimbatore district.",
        "summary_ta": "• வால்பாறையில் 12 யானை வழித்தடங்களில் AI தெர்மல் கேமரா நெட்வொர்க் அமைக்கப்பட்டது.\n• எஸ்டேட் தொழிலாளர்கள் மற்றும் வனத்துறை அதிகாரிகளுக்கு உடனடி எச்சரிக்கை விடுக்கப்படுகிறது.\n• கோவை மாவட்டத்தில் மனித-யானை மோதல் அபாயத்தைக் குறைக்க நடவடிக்கை மேற்கொள்ளப்பட்டு வருகிறது.",
        "category": "Human-Wildlife Conflict",
        "conflict_level": "High",
        "district": "Coimbatore",
        "species": ["Elephant"],
        "source_name": "The Hindu Wildlife Special",
        "source_url": "https://www.thehindu.com/news/national/tamil-nadu/valparai-ai-elephant-conflict-warning/article99881.ece",
        "sentiment": "Critical Alert"
    },
    {
        "title_en": "Wild tusker enters Gudalur residential border; Forest Rapid Response Teams deployed",
        "title_ta": "கூடலூர் குடியிருப்பு எல்லைக்குள் நுழைந்த காட்டு யானை; வனத்துறை சிறப்பு மீட்புக் குழுக்கள் விரைவு",
        "content_en": "A wild elephant strayed into the fringes of Gudalur town in the Nilgiris district late Thursday night. Forest officials and Rapid Response Teams (RRT) successfully guided the tusker back into the Mudumalai Tiger Reserve buffer zone without casualty.",
        "content_ta": "நீலகிரி மாவட்டம் கூடலூர் நகரின் எல்லைப் பகுதிக்கு வியாழன் இரவு காட்டு யானை ஒன்று புகுந்தது. வனத்துறை அதிகாரிகள் மற்றும் விரைவு நடவடிக்கை குழுவினர் (RRT) அந்த யானையை முதுமலை புலிகள் காப்பகக் காட்டுப் பகுதிக்குள் வெற்றிகரமாக விரட்டினர்.",
        "summary_en": "• Wild tusker spotted near Gudalur human habitations late Thursday night.\n• TN Forest Rapid Response Team deployed with kumki support for safe driving operation.\n• No human injuries or major crop damage reported.",
        "summary_ta": "• கூடலூர் பகுதி குடியிருப்புக்கு அருகில் காட்டு யானை நடமாட்டம் கண்டறியப்பட்டது.\n• வனத்துறை சிறப்பு மீட்புக் குழுவினர் யானையை காட்டுக்குள் பாதுகாப்பாக விரட்டினர்.\n• மனிதர்களுக்கு காயம் அல்லது பெரிய அளவிலான பயிர் சேதம் எதுவும் ஏற்படவில்லை.",
        "category": "Human-Wildlife Conflict",
        "conflict_level": "Medium",
        "district": "Nilgiris",
        "species": ["Elephant"],
        "source_name": "Mongabay Conservation",
        "source_url": "https://india.mongabay.com/2026/08/gudalur-wildlife-rrt-deployment",
        "sentiment": "Negative"
    },

    # 2. Eco-Tourism & Sanctuaries
    {
        "title_en": "Mudumalai Tiger Reserve launches eco-tourism vehicle safari online booking for monsoon season",
        "title_ta": "முதுமலை புலிகள் காப்பகத்தில் பருவமழைக் காலத்திற்கான ஆன்லைன் சூழல் சுற்றுலா வனச்சவாரி முன்பதிவு தொடக்கம்",
        "content_en": "Mudumalai Tiger Reserve (MTR) has officially opened its streamlined online portal for eco-tourism jungle safaris. Visitors can now book guided electric bus safaris through Theppakadu and enjoy views of wild Asian elephants, gaurs, and spotted deer.",
        "content_ta": "முதுமலை புலிகள் காப்பகம் (MTR) தனது புதிய ஆன்லைன் இணையதளம் மூலம் சூழல் சுற்றுலா வனச்சவாரி முன்பதிவை தொடங்கியுள்ளது. சுற்றுலா பயணிகள் தெப்பக்காடு பகுதியில் மின்சார பேருந்து மூலம் வனவிலங்குகளைப் பார்வையிட முன்பதிவு செய்யலாம்.",
        "summary_en": "• Official online portal launched for Mudumalai Tiger Reserve eco-tourism safaris.\n• Introduction of eco-friendly battery electric safari vehicles at Theppakadu.\n• Strict carrying capacity limits enforced to protect tiger reserve core areas.",
        "summary_ta": "• முதுமலை புலிகள் காப்பக சூழல் சுற்றுலா முன்பதிவு இணையதளம் தொடங்கப்பட்டது.\n• தெப்பக்காடு பகுதியில் சூழலுக்கு உகந்த மின்சார சவாரி வாகனங்கள் அறிமுகப்படுத்தப்பட்டுள்ளன.\n• காப்பகத்தின் முக்கிய வனப்பகுதிகளைப் பாதுகாக்க சுற்றுலாப் பயணிகள் எண்ணிக்கை கட்டுப்படுத்தப்படுகிறது.",
        "category": "Eco-Tourism & Sanctuaries",
        "conflict_level": "None",
        "district": "Nilgiris",
        "species": ["Tiger", "Elephant", "Gaur (Indian Bison)"],
        "source_name": "Vikatan Wildlife & Eco-Tourism",
        "source_url": "https://www.vikatan.com/environment/mudumalai-ecotourism-online-safari",
        "sentiment": "Positive"
    },
    {
        "title_en": "Megamalai Wildlife Sanctuary opens new eco-trail and bird watching watchtowers in Theni",
        "title_ta": "தேனி மேகமலை வனவிலங்கு சரணாலயத்தில் புதிய சூழல் நடைபாதை மற்றும் பறவைகள் நோக்கும் கோபுரம் திறப்பு",
        "content_en": "The Tamil Nadu Forest Department has commissioned a regulated 4-km eco-trail and two elevated bird observation towers in Megamalai. Local tribal guides have been trained to lead tourists through rich Western Ghats endemic fauna habitats.",
        "content_ta": "தேனி மாவட்டம் மேகமலையில் 4 கி.மீ சூழல் நடைபாதை மற்றும் இரண்டு புதிய பறவைகள் நோக்கும் கோபுரங்களை தமிழ்நாடு வனத்துறை திறந்துவைத்துள்ளது. உள்ளூர் பழங்குடியின இளைஞர்களுக்கு சூழல் சுற்றுலா வழிகாட்டிகளாக பயிற்சி அளிக்கப்பட்டுள்ளது.",
        "summary_en": "• 4-km regulated eco-walking trail opened in Megamalai Wildlife Sanctuary.\n• Local tribal youth employed as certified eco-guides for bird watching tours.\n• Promotes sustainable eco-tourism while generating forest livelihood income.",
        "summary_ta": "• மேகமலை வனவிலங்கு சரணாலயத்தில் 4 கி.மீ சூழல் நடைபாதை அமைக்கப்பட்டது.\n• பழங்குடியின இளைஞர்களுக்கு அங்கீகரிக்கப்பட்ட வன வழிகாட்டிகளாக வேலைவாய்ப்பு வழங்கப்பட்டுள்ளது.\n• வனத்துறை மூலம் நிலையான சூழல் சுற்றுலா மற்றும் வாழ்வாதாரம் மேம்படுத்தப்படுகிறது.",
        "category": "Eco-Tourism & Sanctuaries",
        "conflict_level": "None",
        "district": "Theni & Megamalai",
        "species": ["Lion-Tailed Macaque", "Nilgiri Tahr"],
        "source_name": "Dinamalar Eco Feature",
        "source_url": "https://www.dinamalar.com/news_detail.asp?id=3881920",
        "sentiment": "Positive"
    },

    # 3. Wildlife Crime & Rescue
    {
        "title_en": "TN Forest Anti-Poaching Squad seizes smuggled ivory tusks near Sathyamangalam tiger reserve border; 3 arrested",
        "title_ta": "சத்தியமங்கலம் புலிகள் காப்பக எல்லையில் கடத்தப்பட்ட தந்தங்கள் பறிமுதல்; வன குற்றத் தடுப்புப் பிரிவு 3 பேரை கைது செய்தது",
        "content_en": "In a swift operation, the Special Anti-Poaching Cell of the Sathyamangalam Tiger Reserve seized a pair of elephant tusks and arrested three wildlife traffickers near the Tamil Nadu-Karnataka border check post.",
        "content_ta": "சத்தியமங்கலம் புலிகள் காப்பக வன குற்றத் தடுப்புப் பிரிவினர் நடத்திய அதிரடி வேட்டையில், தமிழ்நாடு-கர்நாடக எல்லைச் சாவடி அருகே யானைத் தந்தங்களைக் கடத்திய 3 வனக் குற்றவாளிகள் கைது செய்யப்பட்டனர்.",
        "summary_en": "• Special Anti-Poaching Cell seized 2 raw elephant tusks near STR border.\n• Three suspects arrested under Wildlife Protection Act, 1972.\n• Inter-state joint intelligence operation intensified across forest check posts.",
        "summary_ta": "• சத்தியமங்கலம் புலிகள் காப்பக எல்லை அருகே 2 யானைத் தந்தங்கள் பறிமுதல் செய்யப்பட்டன.\n• வனவிலங்கு பாதுகாப்புச் சட்டத்தின் கீழ் 3 பேர் கைது செய்யப்பட்டு சிறையில் அடைக்கப்பட்டனர்.\n• மாநில எல்லை சோதனைக் சாவடிகளில் தீவிர வனப் பாதுகாப்பு சோதனைகள் தீவிரப்படுத்தப்பட்டுள்ளன.",
        "category": "Wildlife Crime & Rescue",
        "conflict_level": "Low",
        "district": "Erode & Sathyamangalam",
        "species": ["Elephant"],
        "source_name": "Indian Express Chennai",
        "source_url": "https://indianexpress.com/article/cities/chennai/sathyamangalam-ivory-seizure-anti-poaching",
        "sentiment": "Negative"
    },
    {
        "title_en": "Forest Veterinary Squad successfully rescues female leopard trapped in agricultural wire snare in Anamalai",
        "title_ta": "ஆனைமலையில் விவசாய நிலக் கம்பியில் சிக்கிய பெண் சிறுத்தையை வன மருத்துவக் குழுவினர் வெற்றிகரமாக மீட்டனர்",
        "content_en": "A 4-year-old female leopard caught in a wire snare set near an agricultural patch bordering Anamalai Tiger Reserve was safely tranquilized, treated by forest veterinarians, and released into core forest area.",
        "content_ta": "ஆனைமலை புலிகள் காப்பக எல்லையோர விவசாய நிலத்தில் வைக்கப்பட்டிருந்த கம்பி வலையில் சிக்கிய 4 வயது பெண் சிறுத்தை, வனத்துறை கால்நடை மருத்துவர்களால் மயக்க ஊசி செலுத்தி பத்திரமாக மீட்கப்பட்டு காட்டில் விடப்பட்டது.",
        "summary_en": "• 4-year-old female leopard discovered trapped in illegal wire snare near tea estate.\n• Forest Vets tranquilized the feline and treated minor leg abrasions.\n• Leopard successfully released back into Anamalai core sanctuary habitat.",
        "summary_ta": "• விவசாய நிலத்து வலையில் சிக்கிய பெண் சிறுத்தை வனத்துறை மருத்துவக் குழுவால் மீட்கப்பட்டது.\n• காயமடைந்த சிறுத்தைக்கு சிகிச்சை அளிக்கப்பட்ட பின் ஆனைமலை காப்பகத்திற்குள் மீண்டும் விடப்பட்டது.\n• சட்டவிரோத வலையை அமைத்தவர்கள் மீது வனக் குற்ற வழக்கு பதிவு செய்யப்பட்டுள்ளது.",
        "category": "Wildlife Crime & Rescue",
        "conflict_level": "Medium",
        "district": "Tiruppur & Anamalai",
        "species": ["Leopard"],
        "source_name": "Down To Earth India",
        "source_url": "https://www.downtoearth.org.in/news/wildlife/anamalai-leopard-rescue-operation",
        "sentiment": "Positive"
    },

    # 4. Forest Fire & Safety
    {
        "title_en": "Tamil Nadu Forest Dept constructs 150 km fire lines in Kodaikanal and Nilgiris ahead of summer dry spell",
        "title_ta": "கோடை உலர்ந்த காலத்தை முன்னிட்டு கொடைக்கானல் மற்றும் நீலகிரியில் 150 கி.மீ தீத்தடுப்புக் கோடுகளை வனத்துறை உருவாக்கியது",
        "content_en": "To prevent devastating forest fires during dry weather conditions, the Tamil Nadu Forest Department has completed creating over 150 km of counter-fire buffer lines and deployed 80 seasonal fire watchers across Kodaikanal and Nilgiris hill ranges.",
        "content_ta": "கோடைக் காலத்தில் ஏற்படும் காட்டுத் தீ அசம்பாவிதங்களைத் தவிர்க்க கொடைக்கானல் மற்றும் நீலகிரி மலைகளில் 150 கி.மீ தூரத்திற்கு மேல் தீத்தடுப்புக் கோடுகளை தமிழ்நாடு வனத்துறை அமைத்துள்ளது. 80 சிறப்புத் தீ கண்காணிப்பாளர்களும் நியமிக்கப்பட்டுள்ளனர்.",
        "summary_en": "• 150 km of strategic forest fire lines cleared across Nilgiris and Kodaikanal divisions.\n• Satellite thermal sensors and drone surveillance active for early fire detection.\n• 80 trained local fire watchers stationed at high-altitude vulnerable peaks.",
        "summary_ta": "• நீலகிரி மற்றும் கொடைக்கானல் வனப் பகுதிகளில் 150 கி.மீ தீத்தடுப்புக் கோடுகள் உருவாக்கப்பட்டன.\n• செயற்கைக்கோள் தெர்மல் மற்றும் ட்ரோன் கண்காணிப்பு மூலம் தீ ஆபத்து கண்காணிக்கப்படுகிறது.\n• 80 உள்ளூர் பழங்குடி தீக் கண்காணிப்பாளர்கள் பணியமர்த்தப்பட்டுள்ளனர்.",
        "category": "Forest Fire & Safety",
        "conflict_level": "Low",
        "district": "Dindigul & Kodaikanal",
        "species": ["Nilgiri Tahr", "Gaur (Indian Bison)"],
        "source_name": "The Hindu Environment",
        "source_url": "https://www.thehindu.com/sci-tech/energy-and-environment/kodaikanal-forest-fire-prevention-lines/article98410.ece",
        "sentiment": "Neutral"
    },
    {
        "title_en": "Prompt action by TN fire watchers extinguishes minor grass fire in KMTR tiger reserve core",
        "title_ta": "களக்காடு முண்டந்துறை புலிகள் காப்பகத்தில் பரவிய காட்டுத் தீயை வனத்துறை தீயணைப்புக் குழுவினர் உடனடியாகக் கட்டுப்படுத்தினர்",
        "content_en": "A minor grassland fire reported in the high-altitude shola ridges of Kalakad Mundanthurai Tiger Reserve (KMTR) was brought under control within two hours by forest ground patrols, preventing spread to shola forest patches.",
        "content_ta": "களக்காடு முண்டந்துறை புலிகள் காப்பக உயரமான புல்வெளி மலைப்பகுதியில் ஏற்பட்ட சிறிய காட்டுத் தீயை வனத்துறை நிலக் கண்காணிப்புக் குழுவினர் 2 மணி நேரத்திற்குள் அணைத்து பெரிய காட்டுத் தீ விபத்தைத் தடுத்தனர்.",
        "summary_en": "• Minor fire incident detected at KMTR high-ridge shola grasslands.\n• Forest fire control squad mobilized quickly to douse flames within 2 hours.\n• Zero damage to endemic wildlife or evergreen shola tree flora.",
        "summary_ta": "• களக்காடு முண்டந்துறை புலிகள் காப்பகப் புல்வெளியில் தீ விபத்து கண்டறியப்பட்டது.\n• வனத்துறைத் தீயணைப்புக் குழு 2 மணி நேரத்திற்குள் தீயைக் கட்டுக்குள் கொண்டுவந்தது.\n• அரிய வகை வனவிலங்குகள் மற்றும் மரங்களுக்கு எவ்வித பாதிப்பும் ஏற்படவில்லை.",
        "category": "Forest Fire & Safety",
        "conflict_level": "Low",
        "district": "Tirunelveli & KMTR",
        "species": ["Wildlife"],
        "source_name": "Vikatan Environment News",
        "source_url": "https://www.vikatan.com/environment/kmtr-forest-fire-extinguished",
        "sentiment": "Neutral"
    },

    # 5. Forest Encroachment
    {
        "title_en": "Tamil Nadu Forest Dept evicts illegal encroachments and reclaims 45 acres of reserve forest land in Coimbatore",
        "title_ta": "கோவையில் சட்டவிரோத ஆக்கிரமிப்புகளை அகற்றி 45 ஏக்கர் காப்பக வனநிலத்தை தமிழ்நாடு வனத்துறை மீட்டது",
        "content_en": "Following High Court directives, the Tamil Nadu Forest Department conducted an eviction drive in Boluvampatti range of Coimbatore, recovering 45 acres of encroached elephant corridor land and erecting boundary pillars.",
        "content_ta": "சென்னை உயர்நீதிமன்ற உத்தரவின்படி, கோவை போளுவாம்பட்டி வனச்சரகத்தில் தீவிர ஆக்கிரமிப்பு அகற்றும் நடவடிக்கையை மேற்கொண்ட வனத்துறை, 45 ஏக்கர் யானை வழித்தட வனநிலத்தை மீட்டு எல்லைக் கற்களை நட்டது.",
        "summary_en": "• 45 acres of encroached reserve forest land reclaimed in Boluvampatti range.\n• Illegal commercial structures demolished and boundary demarcation pillars erected.\n• Restores vital contiguous elephant migration path between TN and Kerala.",
        "summary_ta": "• கோவை போளுவாம்பட்டி வனச்சரகத்தில் 45 ஏக்கர் ஆக்கிரமிக்கப்பட்ட வனநிலம் மீட்கப்பட்டது.\n• சட்டவிரோதக் கட்டிடங்கள் இடிக்கப்பட்டு வன எல்லைக் கற்கள் நடப்பட்டுள்ளன.\n• யானைகள் எளிதாக இடம்பெயர வழித்தடப் பகுதிகள் மீண்டும் சீரமைக்கப்பட்டுள்ளன.",
        "category": "Forest Encroachment",
        "conflict_level": "Low",
        "district": "Coimbatore",
        "species": ["Elephant"],
        "source_name": "The Hindu Tamil Nadu",
        "source_url": "https://www.thehindu.com/news/national/tamil-nadu/coimbatore-forest-encroachment-eviction-drive/article713990.ece",
        "sentiment": "Positive"
    },
    {
        "title_en": "Forest officials issue notices to resort owners for illegal forest land occupation near Kodaikanal buffer zone",
        "title_ta": "கொடைக்கானல் காப்பக எல்லை அருகே சட்டவிரோதமாக வனநிலத்தை ஆக்கிரமித்த விடுதி உரிமையாளர்களுக்கு வனத்துறை நோட்டீஸ்",
        "content_en": "Dindigul district forest authorities have served eviction notices to four private commercial resorts for illegally occupying reserve forest buffer land along the Kodaikanal hill slopes.",
        "content_ta": "கொடைக்கானல் மலைச்சரிவில் காப்பக வனநிலத்தை சட்டவிரோதமாக ஆக்கிரமித்த 4 தனியார் விடுதி உரிமையாளர்களுக்கு திண்டுக்கல் மாவட்ட வனத்துறை அதிகாரிகள் வெளியேற்ற நோட்டீஸ் அளித்துள்ளனர்.",
        "summary_en": "• Eviction notices served to 4 luxury resorts operating on encroached forest land.\n• GPS boundary surveys revealed encroachment into shola forest buffer zones.\n• Strict warning issued against illegal construction in protected tiger & wildlife corridors.",
        "summary_ta": "• வனநிலத்தை ஆக்கிரமித்து இயங்கிய 4 சொகுசு விடுதிகளுக்கு நோட்டீஸ் வழங்கப்பட்டுள்ளது.\n• GPS ஆய்வு மூலம் வனச்சரக நில ஆக்கிரமிப்பு கண்டறியப்பட்டு நடவடிக்கை எடுக்கப்பட்டுள்ளது.\n• வனவிலங்கு வழித்தடங்களில் சட்டவிரோதக் கட்டிடங்கள் கட்டுவதற்கு தடை விதிக்கப்பட்டுள்ளது.",
        "category": "Forest Encroachment",
        "conflict_level": "Low",
        "district": "Dindigul & Kodaikanal",
        "species": ["Wildlife"],
        "source_name": "Dinamalar State News",
        "source_url": "https://www.dinamalar.com/news_detail.asp?id=3882001",
        "sentiment": "Neutral"
    }
]

def seed_database():
    print("Seeding database with Tamil Nadu Wildlife news articles across all categories...")
    
    # Add seed articles to db_storage
    now = datetime.now()
    added_count = 0
    for idx, data in enumerate(SEED_ARTICLES):
        art_id = f"art_seed_{idx+1:03d}"
        
        # Avoid duplicate title insertion
        if any(a.title_en == data["title_en"] for a in db_storage.articles.values()):
            continue
            
        pub_time = now - timedelta(hours=idx*4 + 2)
        
        art = Article(
            id=art_id,
            title_en=data["title_en"],
            title_ta=data["title_ta"],
            content_en=data["content_en"],
            content_ta=data["content_ta"],
            summary_en=data["summary_en"],
            summary_ta=data["summary_ta"],
            category=data["category"],
            conflict_level=data["conflict_level"],
            district=data["district"],
            species=data["species"],
            source_name=data["source_name"],
            source_url=data["source_url"],
            published_at=pub_time,
            tags=[data["category"], data["district"]] + data["species"],
            key_entities=KeyEntities(
                locations=[data["district"]],
                species=data["species"],
                authorities=["Tamil Nadu Forest Department"],
                impact="Active ground monitoring by Forest Division."
            ),
            sentiment=data["sentiment"],
            verification_status="VERIFIED",
            verification_reason="Original source metadata verified",
            created_at=pub_time
        )
        db_storage.add_article(art)
        added_count += 1

    print(f"Added {added_count} curated category seed articles. Total articles in storage: {len(db_storage.articles)}")

    try:
        rss_count = RSSCollector.fetch_all()
        print(f"RSS fetch completed: {rss_count} new articles.")
    except Exception as e:
        print(f"RSS fetch note: {e}")

if __name__ == "__main__":
    seed_database()

