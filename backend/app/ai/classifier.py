import os
import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from app.models.schemas import KeyEntities

logger = logging.getLogger(__name__)

DISTRICT_KEYWORDS = {
    "Coimbatore": ["coimbatore", "valparai", "pollachi", "boluvampatti", "mettupalayam", "thondamuthur", "marudhamalai", "கோவை", "வால்பாறை"],
    "Nilgiris": ["nilgiris", "ooty", "udhagamandalam", "coonoor", "gudalur", "kotagiri", "mudumalai", "pykara", "நீலகிரி", "ஊட்டி", "கூடலூர்"],
    "Erode & Sathyamangalam": ["sathyamangalam", "str", "bhavanisagar", "erode", "hasanur", "thalavadi", "ஈரோடு", "சத்தியமங்கலம்"],
    "Tiruppur & Anamalai": ["anamalai", "atr", "udumalpet", "tiruppur", "amaravathi", "ஆனைமலை", "திருப்பூர்"],
    "Theni & Megamalai": ["megamalai", "theni", "cumbum", "andipatti", "periyar", "தேனி", "மேகமலை"],
    "Dindigul & Kodaikanal": ["kodaikanal", "dindigul", "palani", "sirumalai", "திண்டுக்கல்", "கொடைக்கானல்"],
    "Tirunelveli & KMTR": ["kalakad", "mundanthurai", "kmtr", "tirunelveli", "papanasam", "manjolai", "திருநெல்வேலி", "களக்காடு"],
    "Kanyakumari": ["kanyakumari", "pechiparai", "marunthuvazh malai", "asambu", "கன்னியாகுமரி"],
    "Dharmapuri & Krishnagiri": ["dharmapuri", "krishnagiri", "hogenakkal", "denkanikottai", "hosur", "cauvery north", "தர்மபுரி", "கிருஷ்ணகிரி"],
    "Salem & Yercaud": ["salem", "shevaroys", "yercaud", "mettur", "சேலம்", "ஏற்காடு"],
    "Ramanathapuram & Gulf of Mannar": ["ramanathapuram", "gulf of mannar", "dugong", "rameshwaram", "இராமநாதபுரம்"],
    "Chennai & Vandalur": ["chennai", "vandalur", "guindy", "nanmangalam", "சென்னை", "வண்டலூர்"],
    "Chengalpattu & Vedanthangal": ["chengalpattu", "vedanthangal", "karikili", "காஞ்சிபுரம்", "செங்கல்பட்டு"],
    "Nagapattinam & Point Calimere": ["nagapattinam", "point calimere", "kodiyakarai", "கொடாய்க்கரை", "நாகப்பட்டினம்"],
    "Tiruchirappalli & Namakkal": ["tiruchirappalli", "trichy", "namakkal", "kolli hills", "கொல்லிமலை", "திருச்சி"],
    "Tiruvannamalai & Vellore": ["tiruvannamalai", "vellore", "jawadhu hills", "javadi", "ஜவாது மலை", "திருவண்ணாமலை"],
    "Thanjavur & Tiruvarur": ["thanjavur", "tiruvarur", "muthupet", "மன்னார்குடி", "தஞ்சாவூர்"],
    "Tenkasi & Virudhunagar": ["tenkasi", "courtallam", "virudhunagar", "grizzled squirrel", "தென்காசி", "விருதுநகர்"],
    "Villupuram & Cuddalore": ["villupuram", "cuddalore", "pitchavaram", "mangrove", "பிச்சாவரம்", "கடலூர்"]
}

SPECIES_KEYWORDS = {
    "Elephant": ["elephant", "tusker", "makna", "herd", "wild elephant", "ஆனை", "யானை", "காட்டு யானை"],
    "Tiger": ["tiger", "tigress", "panthera tigris", "stripes", "புலி", "சிறுத்தை புலி"],
    "Leopard": ["leopard", "panther", "spotted cat", "சிறுத்தை"],
    "Gaur (Indian Bison)": ["gaur", "bison", "indian bison", "காட்டெருமை"],
    "Wild Boar": ["wild boar", "boar", "swine", "காட்டுப்பன்றி"],
    "Sloth Bear": ["sloth bear", "bear", "கரடி"],
    "Nilgiri Tahr": ["tahr", "nilgiri tahr", "varaiyaadu", "வரைஆடு"],
    "Crocodile": ["crocodile", "mugger", "gharial", "முதலை"],
    "Lion-Tailed Macaque": ["lion-tailed macaque", "ltm", "macaque", "சிங்கம் போன்ற வாலுள்ள குரங்கு"],
    "Sea Turtle": ["turtle", "olive ridley", "sea turtle", "ஆமை", "கடல் ஆமை"],
    "Dhole (Wild Dog)": ["dhole", "wild dog", "cuon alpinus", "செந்நாய்"]
}

CONFLICT_KEYWORDS = {
    "High": ["killed", "fatal", "attacked", "trampled", "died", "crop raid", "destroyed houses", "human casualty", "emergency", "உயிரிழப்பு", "தாக்கியது", "பலி"],
    "Medium": ["strayed", "entered village", "panic", "blocked traffic", "chased", "damage to crops", "forest guards deployed", "ஊருக்குள் புகுந்தது", "பீதி"],
    "Low": ["spotted", "sighted", "crossing road", "monitored", "peaceful", "seen near forest border", "காணப்பட்டது"]
}

CATEGORY_KEYWORDS = {
    "Human-Wildlife Conflict": ["conflict", "human wildlife conflict", "human conflict", "man animal conflict", "attack", "crop raid", "strayed", "villagers", "casualty", "trampled", "compensation", "fencing", "animal movement", "human animal", "man animal", "மக்களுக்கும் விலங்குகளுக்கும் மோதல்", "தாக்குதல்"],
    "Wildlife Crime & Rescue": ["poaching", "poachers", "arrested", "smuggling", "ivory", "tiger skin", "venom", "illegal snare", "wildlife crime", "illegal wildlife trade", "seizure", "seized", "contraband", "வேட்டை", "கைது", "rescued", "captured", "tranquilized", "relocated", "rehab", "treated", "snared", "trapped", "rescue", "evacuated", "medical assistance", "மீட்ப்பு", "பராமரிப்பு", "crime", "trapping"],
    "Forest Fire & Safety": ["forest fire", "wildfire", "fire breakout", "fire alert", "smoke", "burning forest", "fire line", "firefighters", "firefighting", "blaze", "forest blaze", "காடு தீ", "அக்னி", "தீ"],
    "Forest Encroachment": ["encroachment", "forest encroachment", "illegal encroachment", "eviction", "land grab", "illegal occupation", "patta", "encroached forest", "aakkiramippu", "ஆக்கிரமிப்பு", "நில ஆக்கிரமிப்பு", "encourgment", "encouragment"],
    "Eco-Tourism & Sanctuaries": ["eco tourism", "ecotourism", "safari", "tourists", "tourism", "reserve", "national park", "tiger reserve", "visiting hours", "protected area", "protected areas", "biosphere reserve", "wildlife sanctuary", "சுற்றுலா", "சரணாலயம்"],
    "Species Conservation": ["census", "population increase", "breeding", "biodiversity", "conservation", "endangered", "tahr day", "habitat protection", "பாதுகாப்பு", "அரிதான"],
    "Forest Dept & Policy": ["forest department", "officials", "patrol", "wildlife act", "chief wildlife warden", "forest policy", "policy development", "வனத்துறை", "அரசு"]
}

TAMIL_NADU_LOCATIONS = [
    "tamil nadu", "tamilnadu", "tn forest", "tn police", "tnfwccb", "madras", "chennai", "தமிழ்நாடு", "வனத்துறை",
    "coimbatore", "valparai", "pollachi", "boluvampatti", "mettupalayam", "thondamuthur", "marudhamalai", "கோவை", "வால்பாறை", "பொள்ளாச்சி", "மேட்டுப்பாளையம்",
    "nilgiris", "ooty", "udhagamandalam", "coonoor", "gudalur", "kotagiri", "mudumalai", "pykara", "நீலகிரி", "ஊட்டி", "கூடலூர்", "முதுமலை",
    "sathyamangalam", "str", "bhavanisagar", "erode", "hasanur", "thalavadi", "ஈரோடு", "சத்தியமங்கலம்",
    "anamalai", "atr", "udumalpet", "tiruppur", "amaravathi", "ஆனைமலை", "திருப்பூர்", "உடுமலைப்பேட்டை",
    "megamalai", "theni", "cumbum", "andipatti", "periyar", "தேனி", "மேகமலை", "கம்பம்",
    "kodaikanal", "dindigul", "palani", "sirumalai", "திண்டுக்கல்", "கொடைக்கானல்", "பழனி",
    "kalakad", "mundanthurai", "kmtr", "tirunelveli", "papanasam", "manjolai", "திருநெல்வேலி", "களக்காடு", "பாபநாசம்",
    "kanyakumari", "pechiparai", "marunthuvazh malai", "asambu", "கன்னியாகுமரி",
    "dharmapuri", "krishnagiri", "hogenakkal", "denkanikottai", "hosur", "cauvery north", "தர்மபுரி", "கிருஷ்ணகிரி", "ஓசூர்", "ஒகேனக்கல்",
    "salem", "shevaroys", "yercaud", "mettur", "சேலம்", "ஏற்காடு", "மேட்டூர்",
    "ramanathapuram", "gulf of mannar", "dugong", "rameshwaram", "இராமநாதபுரம்", "இராமேஸ்வரம்",
    "vandalur", "guindy", "nanmangalam", "சென்னை", "வண்டலூர்", "கிண்டி",
    "chengalpattu", "vedanthangal", "karikili", "காஞ்சிபுரம்", "செங்கல்பட்டு", "வேடந்தாங்கல்",
    "nagapattinam", "point calimere", "kodiyakarai", "கொடாய்க்கரை", "நாகப்பட்டினம்",
    "tiruchirappalli", "trichy", "namakkal", "kolli hills", "கொல்லிமலை", "திருச்சி", "நாமக்கல்",
    "tiruvannamalai", "vellore", "jawadhu hills", "javadi", "ஜவாது மலை", "திருவண்ணாமலை", "வேலூர்",
    "thanjavur", "tiruvarur", "muthupet", "மன்னார்குடி", "தஞ்சாவூர்", "திருவாரூர்",
    "tenkasi", "courtallam", "virudhunagar", "தென்காசி", "குற்றாலம்", "விருதுநகர்",
    "villupuram", "cuddalore", "pitchavaram", "பிச்சாவரம்", "கடலூர்", "விழுப்புரம்",
    "madurai", "sivaganga", "pudukkottai", "thoothukudi", "tuticorin", "karur", "perambalur", "ariyalur", "ranipet", "tirupathur", "kallakurichi", "mayiladuthurai",
    "மதுரை", "சிவகங்கை", "புதுக்கோட்டை", "தூத்துக்குடி", "கரூர்", "பெரம்பலூர்", "அரியலூர்", "ராணிப்பேட்டை", "திருப்பத்தூர்", "கள்ளக்குறிச்சி", "மயிலாடுதுறை"
]

SEMANTIC_FAUNA_CONCEPTS = {
    "elephant", "tusker", "makna", "herd", "wild elephant", "ஆனை", "யானை", "காட்டு யானை",
    "tiger", "tigress", "panthera tigris", "stripes", "புலி", "சிறுத்தை புலி",
    "leopard", "panther", "spotted cat", "சிறுத்தை",
    "gaur", "bison", "indian bison", "காட்டெருமை",
    "wild boar", "boar", "swine", "காட்டுப்பன்றி",
    "sloth bear", "bear", "கரடி",
    "tahr", "nilgiri tahr", "varaiyaadu", "வரைஆடு",
    "crocodile", "mugger", "gharial", "முதலை",
    "macaque", "lion-tailed macaque", "ltm", "சிங்கம் போன்ற வாலுள்ள குரங்கு",
    "sea turtle", "turtle", "olive ridley", "ஆமை", "கடல் ஆமை",
    "dugong", "sea cow", "dhole", "wild dog", "செந்நாய்",
    "pangolin", "hornbill", "king cobra", "python", "vulture", "loris", "sloth",
    "deer", "sambar", "chital", "spotted deer", "barking deer", "wild animal", "wild species",
    "fauna", "carnivore", "herbivore", "mammal", "reptile", "avian", "raptor", "endangered species",
    "wildlife", "wild animal", "wild beasts", "விலங்கு", "பறவை", "காட்டு உயிரினங்கள்"
}

SEMANTIC_HABITAT_CONCEPTS = {
    "forest", "jungle", "sanctuary", "tiger reserve", "reserve", "national park", "biosphere",
    "elephant corridor", "corridor", "shola", "mangrove", "wetland", "protected area",
    "forest range", "forest division", "forest beat", "canopy", "timber", "wilderness",
    "காடு", "வனம்", "வனப்பகுதி", "காப்பகம்", "சரணாலயம்", "உயிர்க்கோளம்"
}

SEMANTIC_CONSERVATION_CONCEPTS = {
    "poaching", "anti-poaching", "snare", "ivory", "tiger skin", "venom", "wildlife crime",
    "rescue", "rescued", "tranquilized", "relocated", "rehabilitation", "rehab", "camera trap",
    "census", "population count", "forest fire", "wildfire", "fire line", "blaze", "firefighting",
    "human-wildlife", "human animal", "man animal", "conflict", "crop raid", "trampled",
    "forest department", "forest dept", "forest guard", "forest ranger", "chief wildlife warden",
    "tnfwccb", "rrt", "rapid response team", "eco-tourism", "safari", "forest policy",
    "wildlife act", "encroachment", "eviction", "habitat protection", "biodiversity",
    "வனத்துறை", "வேட்டை", "கைது", "மீட்ப்பு", "தீ", "அக்னி", "ஆக்கிரமிப்பு", "பாதுகாப்பு"
}

SEMANTIC_DISTRACTORS = {
    "ppfm spraying", "crop spraying", "fertilizer subsidy", "paddy procurement", "sugarcane price",
    "revenue receipts", "liquor sales", "quota to muslim converts", "drought-proofing", "heatwaves and lightning",
    "farm spraying", "agricultural subsidy", "kisan credit", "election campaign", "political party",
    "municipal budget", "traffic police", "it park", "real estate", "stock market", "film release"
}


def _extract_text(article: Any, content: Optional[str] = None) -> Tuple[str, str]:
    """Helper to cleanly unpack title and content from string, dict, or Pydantic model."""
    if isinstance(article, str):
        return article, content or ""
    
    title_text = ""
    content_text = ""

    if hasattr(article, "title_en"):
        title_en = getattr(article, "title_en", "") or ""
        title_ta = getattr(article, "title_ta", "") or ""
        title_text = f"{title_en} {title_ta}".strip()
        
        content_en = getattr(article, "content_en", "") or ""
        content_ta = getattr(article, "content_ta", "") or ""
        content_text = f"{content_en} {content_ta}".strip()
    elif isinstance(article, dict):
        title_text = f"{article.get('title_en', '')} {article.get('title_ta', '')} {article.get('title', '')}".strip()
        content_text = f"{article.get('content_en', '')} {article.get('content_ta', '')} {article.get('content', '')}".strip()
    
    return title_text, content_text


def is_tamil_nadu(article: Any, content: Optional[str] = None) -> bool:
    """
    Determines if an article is geographically or institutionally relevant to Tamil Nadu.
    Accepts an Article schema instance, dict, or string title (with optional content).
    """
    title_text, content_text = _extract_text(article, content)
    text = f"{title_text} {content_text}".lower().strip()
    if not text:
        return False

    return any(loc in text for loc in TAMIL_NADU_LOCATIONS)


def is_wildlife_or_forest(article: Any, content: Optional[str] = None) -> bool:
    """
    Determines if an article is semantically relevant to Forest or Wildlife topics.
    Uses OpenAI semantic classification if API key is configured, or multi-dimensional
    local semantic concept density and relevance engine.
    """
    title_text, content_text = _extract_text(article, content)
    text = f"{title_text} {content_text}".lower().strip()
    if not text:
        return False

    # Check for hard distractor topics (pure non-wildlife agriculture/politics/finance)
    if any(dis in text for dis in SEMANTIC_DISTRACTORS):
        strong_fauna_count = sum(1 for word in SEMANTIC_FAUNA_CONCEPTS if word in text)
        if strong_fauna_count == 0:
            return False

    # OpenAI zero-shot semantic call if API key present
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        try:
            import httpx
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a semantic article relevance classifier for a Wildlife & Forest Intelligence platform. "
                            "Determine if the article title and text are semantically focused on wildlife, fauna, flora, "
                            "forest department operations, habitat conservation, human-wildlife encounters, poaching, "
                            "forest fires, or eco-tourism. "
                            "Return JSON with key 'is_wildlife_or_forest' (boolean) and 'confidence' (float 0.0-1.0)."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title_text}\nContent: {content_text}"
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }
            res = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                timeout=3.0
            )
            if res.status_code == 200:
                data = res.json()
                parsed = json.loads(data['choices'][0]['message']['content'])
                if "is_wildlife_or_forest" in parsed:
                    return bool(parsed["is_wildlife_or_forest"])
        except Exception as e:
            logger.debug(f"OpenAI semantic check skipped/failed: {e}")

    # Local Semantic Concept Density Scoring Engine
    fauna_score = sum(1 for kw in SEMANTIC_FAUNA_CONCEPTS if kw in text)
    habitat_score = sum(1 for kw in SEMANTIC_HABITAT_CONCEPTS if kw in text)
    conservation_score = sum(1 for kw in SEMANTIC_CONSERVATION_CONCEPTS if kw in text)

    total_semantic_score = fauna_score * 2.0 + habitat_score * 1.5 + conservation_score * 1.5

    return total_semantic_score >= 1.5


class ArticleClassifier:
    @staticmethod
    def is_tamil_nadu(article: Any, content: Optional[str] = None) -> bool:
        return is_tamil_nadu(article, content)

    @staticmethod
    def is_tamil_nadu_relevant(title: str, content: str = "") -> bool:
        return is_tamil_nadu(title, content)

    @staticmethod
    def is_wildlife_or_forest(article: Any, content: Optional[str] = None) -> bool:
        return is_wildlife_or_forest(article, content)

    @staticmethod
    def is_forest_or_wildlife_relevant(title: str, content: str = "") -> bool:
        return is_wildlife_or_forest(title, content)

    @staticmethod
    def compute_date_status(published_at) -> str:
        from datetime import datetime, timedelta
        if not published_at:
            return "TODAY"
        today = datetime.now().date()
        if isinstance(published_at, datetime):
            pub_date = published_at.date()
        elif hasattr(published_at, "date"):
            pub_date = published_at.date()
        else:
            pub_date = today

        if pub_date >= today:
            return "TODAY"
        elif pub_date == today - timedelta(days=1):
            return "YESTERDAY"
        else:
            return "OLD"

    @staticmethod
    def classify(title: str, content: str, published_at=None) -> Dict:
        text = f"{title} {content}".lower()

        # Date status calculation
        date_status = ArticleClassifier.compute_date_status(published_at)

        detected_district = "Tamil Nadu"
        for district, keywords in DISTRICT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected_district = district
                break

        detected_species = []
        for species, keywords in SPECIES_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected_species.append(species)
        if not detected_species:
            detected_species = ["Wildlife"]

        conflict_level = "Low"
        for level, keywords in CONFLICT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                conflict_level = level
                break

        detected_category = "General Wildlife"
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected_category = category
                break

        authorities = []
        if "forest department" in text or "forest dept" in text or "வனத்துறை" in text:
            authorities.append("Tamil Nadu Forest Department")
        if "tnfwccb" in text or "crime control bureau" in text or "வனவிலங்கு குற்றம்" in text:
            authorities.append("TN Forest Wildlife Crime Control Bureau (TNFWCCB)")
        if "police" in text or "காவல்" in text:
            authorities.append("Tamil Nadu Police")
        if "court" in text or "high court" in text or "நீதிமன்றம்" in text:
            authorities.append("Madras High Court")

        impact = "Minor disturbance"
        if conflict_level == "High":
            impact = "Severe conflict event"
        elif conflict_level == "Medium":
            impact = "Local alert & monitoring required"

        sentiment = "Neutral"
        if conflict_level in ["High", "Medium"] or "poaching" in text:
            sentiment = "Critical Alert" if conflict_level == "High" else "Negative"
        elif "rescued" in text or "census" in text or "population increase" in text:
            sentiment = "Positive"

        key_entities = KeyEntities(
            locations=[detected_district],
            species=detected_species,
            authorities=authorities if authorities else ["Tamil Nadu Wildlife Division"],
            impact=impact
        )

        return {
            "category": detected_category,
            "conflict_level": conflict_level,
            "district": detected_district,
            "species": detected_species,
            "key_entities": key_entities,
            "sentiment": sentiment,
            "date_status": date_status
        }
