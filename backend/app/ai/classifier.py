import re
from typing import Dict, List, Tuple
from app.models.schemas import KeyEntities

DISTRICT_KEYWORDS = {
    "Coimbatore": ["coimbatore", "valparai", "pollachi", "boluvampatti", "mettupalayam", "thondamuthur", "marudhamalai", "கோவை", "வால்பாறை"],
    "Nilgiris": ["nilgiris", "ooty", "udhagamandalam", "coonoor", "gudalur", "kotagiri", "mudumalai", "pykara", "நீலகிரி", "ஊட்டி", "கூடலூர்"],
    "Erode & Sathyamangalam": ["sathyamangalam", "str", "bhavanisagar", "erode", "hasanur", "thalavadi", "ஈரோடு", "சத்தியமங்கலம்"],
    "Tiruppur & Anamalai": ["anamalai", "atr", "udumalpet", "tiruppur", "amaravathi", "ஆனைமலை", "திருப்பூர்"],
    "Theni & Megamalai": ["megamalai", "theni", "cumbum", "andipatti", "periyar", "தேனி", "மேகமலை"],
    "Dindigul & Kodaikanal": ["kodaikanal", "dindigul", "palani", "sirumalai", "திண்டுக்கல்", "கொடைக்கானல்"],
    "Tirunelveli & KMTR": ["kalakad", "mundanthurai", "kmtr", "tirunelveli", "papanasam", "manjolai", "திருநெல்வேலி", "களக்காடு"],
    "Kanyakumari": ["kanyakumari", "pechiparai", "marunthuvazh malai", "asambu", "கன்னியாகுமரி"],
    "Dharmapuri & Krishnagiri": ["dharmapuri", "krishnagiri", "hogenakkal", "denkanikottai", "cauvery north", "தர்மபுரி", "கிருஷ்ணகிரி"],
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

class ArticleClassifier:
    @staticmethod
    def is_tamil_nadu_relevant(title: str, content: str) -> bool:
        text = f"{title} {content}".lower()
        tn_keywords = [
            "tamil nadu", "tamilnadu", "tn forest", "madras", "chennai", "தமிழ்நாடு", "வனத்துறை",
            "coimbatore", "valparai", "pollachi", "boluvampatti", "mettupalayam", "thondamuthur", "marudhamalai", "கோவை", "வால்பாறை",
            "nilgiris", "ooty", "udhagamandalam", "coonoor", "gudalur", "kotagiri", "mudumalai", "pykara", "நீலகிரி", "ஊட்டி", "கூடலூர்",
            "sathyamangalam", "str", "bhavanisagar", "erode", "hasanur", "thalavadi", "ஈரோடு", "சத்தியமங்கலம்",
            "anamalai", "atr", "udumalpet", "tiruppur", "amaravathi", "ஆனைமலை", "திருப்பூர்",
            "megamalai", "theni", "cumbum", "andipatti", "periyar", "தேனி", "மேகமலை",
            "kodaikanal", "dindigul", "palani", "sirumalai", "திண்டுக்கல்", "கொடைக்கானல்",
            "kalakad", "mundanthurai", "kmtr", "tirunelveli", "papanasam", "manjolai", "திருநெல்வேலி", "களக்காடு",
            "kanyakumari", "pechiparai", "marunthuvazh malai", "asambu", "கன்னியாகுமரி",
            "dharmapuri", "krishnagiri", "hogenakkal", "denkanikottai", "hosur", "cauvery north", "தர்மபுரி", "கிருஷ்ணகிரி",
            "salem", "shevaroys", "yercaud", "mettur", "சேலம்", "ஏற்காடு",
            "ramanathapuram", "gulf of mannar", "dugong", "rameshwaram", "இராமநாதபுரம்",
            "vandalur", "guindy", "nanmangalam", "சென்னை", "வண்டலூர்",
            "chengalpattu", "vedanthangal", "karikili", "காஞ்சிபுரம்", "செங்கல்பட்டு",
            "nagapattinam", "point calimere", "kodiyakarai", "கொடாய்க்கரை", "நாகப்பட்டினம்",
            "tiruchirappalli", "trichy", "namakkal", "kolli hills", "கொல்லிமலை", "திருச்சி",
            "tiruvannamalai", "vellore", "jawadhu hills", "javadi", "ஜவாது மலை", "திருவண்ணாமலை",
            "thanjavur", "tiruvarur", "muthupet", "மன்னார்குடி", "தஞ்சாவூர்",
            "tenkasi", "courtallam", "virudhunagar", "தென்காசி", "விருதுநகர்",
            "villupuram", "cuddalore", "pitchavaram", "பிச்சாவரம்", "கடலூர்"
        ]
        return any(kw in text for kw in tn_keywords)

    @staticmethod
    def is_forest_or_wildlife_relevant(title: str, content: str) -> bool:
        text = f"{title} {content}".lower()

        # Explicitly exclude pure farming/crop-spraying/budget/non-wildlife news
        farm_exclusions = [
            "ppfm spraying", "crop spraying", "fertilizer subsidy", "paddy procurement", "sugarcane price",
            "revenue receipts", "liquor sales", "quota to muslim converts", "drought-proofing", "heatwaves and lightning",
            "farm spraying", "agricultural subsidy", "kisan credit"
        ]
        if any(ex in text for ex in farm_exclusions):
            return False

        wildlife_keywords = [
            "wildlife", "forest department", "forest dept", "forest guard", "sanctuary", "reserve", "national park",
            "protected area", "protected areas", "biosphere reserve", "wildlife sanctuary", "forest fire", "wildfire", "fire alert", "firefighting", "blaze",
            "tiger", "leopard", "elephant", "gaur", "wild boar", "sloth bear", "tahr", "crocodile", "macaque",
            "poaching", "wildlife crime", "seizure", "seized", "illegal wildlife trade", "animal", "rescue", "habitat", "biodiversity", "conservation", "anti-poaching", "patrol",
            "forest policy", "policy development", "encroachment", "forest encroachment", "illegal encroachment", "human-wildlife", "human animal", "human conflict", "man animal", "village", "crop raid", "attack",
            "trapped", "relocated", "wild animal", "forest range", "animal movement", "wildlife act", "eco tourism", "ecotourism", "safari", "tourist",
            "வனத்துறை", "காட்டு", "விலங்கு", "புலி", "யானை", "சிறுத்தை", "காட்டுப்பன்றி", "கரடி", "ஆமை", "பராமரிப்பு", "அக்னி", "தீ", "சுற்றுலா", "ஆக்கிரமிப்பு"
        ]
        return any(kw in text for kw in wildlife_keywords)

    @staticmethod
    def classify(title: str, content: str) -> Dict:
        text = f"{title} {content}".lower()

        # 1. District Identification
        detected_district = "Tamil Nadu (State Wide)"
        for dist, keywords in DISTRICT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected_district = dist
                break

        # 2. Species Identification
        detected_species = []
        for species, keywords in SPECIES_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected_species.append(species)
        if not detected_species:
            detected_species = ["Wildlife"]

        # 3. Conflict Level
        conflict_level = "None"
        for level, keywords in CONFLICT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                conflict_level = level
                break

        # 4. Category Identification
        detected_category = "General Wildlife"
        max_score = 0
        for cat, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > max_score:
                max_score = score
                detected_category = cat

        # 5. Key Entities Extraction
        authorities = []
        if "forest department" in text or "வனத்துறை" in text:
            authorities.append("Tamil Nadu Forest Department")
        if "police" in text or "காவல்துறை" in text:
            authorities.append("Tamil Nadu Police")
        if "rapid response team" in text or "rrt" in text:
            authorities.append("TN Forest Rapid Response Team")

        impact = "No reported human casualties."
        if conflict_level == "High":
            impact = "High severity conflict: Human casualty or major agricultural loss in TN."
        elif conflict_level == "Medium":
            impact = "Moderate disruption: Animal movement monitored by TN forest squad."

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

        # Date status calculation according to user specification
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
