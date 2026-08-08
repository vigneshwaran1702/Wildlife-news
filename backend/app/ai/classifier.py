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
    "Salem": ["salem", "shevaroys", "yercaud", "mettur", "சேலம்", "ஏற்காடு"],
    "Ramanathapuram & Gulf of Mannar": ["ramanathapuram", "gulf of mannar", "dugong", "rameshwaram", "இராமநாதபுரம்"]
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
    "Human-Wildlife Conflict": ["conflict", "attack", "crop raid", "strayed", "villagers", "casualty", "trampled", "compensation", "fencing", "மக்களுக்கும் விலங்குகளுக்கும் மோதல்", "தாக்குதல்"],
    "Rescue & Rehabilitation": ["rescued", "captured", "tranquilized", "relocated", "rehab", "treated", "snared", "trapped", "மீட்பு", "பராமரிப்பு"],
    "Forest Dept & Policy": ["forest department", "officials", "patrol", "sanctuary", "anti-poaching", "wildlife act", "chief wildlife warden", "வனத்துறை", "அரசு"],
    "Species Conservation": ["census", "population increase", "breeding", "biodiversity", "conservation", "endangered", "tahr day", "பாதுகாப்பு", "அரிதான"],
    "Anti-Poaching & Crime": ["poaching", "poachers", "arrested", "smuggling", "ivory", "tiger skin", "venom", "illegal snare", "வேட்டை", "கைது"],
    "Eco-Tourism & Sanctuaries": ["safari", "tourists", "reserve", "national park", "tiger reserve", "visiting hours", "சுற்றுலா", "சரணாலயம்"]
}

class ArticleClassifier:
    @staticmethod
    def is_tamil_nadu_relevant(title: str, content: str) -> bool:
        text = f"{title} {content}".lower()
        tn_keywords = [
            "tamil nadu", "tamilnadu", "tn forest", "தமிழ்நாடு", "வனத்துறை",
            "coimbatore", "valparai", "pollachi", "mettupalayam", " thondamuthur", " கோவை", "வால்பாறை",
            "nilgiris", "ooty", "coonoor", "gudalur", "mudumalai", "mukurthi", "நீலகிரி", "ஊட்டி", "கூடலூர்",
            "sathyamangalam", "str", "bhavanisagar", "erode", "hasanur", "thalavadi", "ஈரோடு", "சத்தியமங்கலம்",
            "anamalai", "atr", "udumalpet", "tiruppur", "ஆனைமலை", "திருப்பூர்",
            "megamalai", "theni", "cumbum", "தேனி", "மேகமலை",
            "kodaikanal", "dindigul", "palani", "sirumalai", "திண்டுக்கல்", "கொடைக்கானல்",
            "kalakad", "mundanthurai", "kmtr", "tirunelveli", "papanasam", "திருநெல்வேலி", "களக்காடு",
            "kanyakumari", "pechiparai", "கன்னியாகுமரி",
            "dharmapuri", "krishnagiri", "hogenakkal", "denkanikottai", "தர்மபுரி", "கிருஷ்ணகிரி",
            "salem", "yercaud", "mettur", "சேலம்", "ஏற்காடு",
            "ramanathapuram", "gulf of mannar", "rameshwaram", "இராமநாதபுரம்"
        ]
        return any(kw in text for kw in tn_keywords)

    @staticmethod
    def is_forest_or_wildlife_relevant(title: str, content: str) -> bool:
        text = f"{title} {content}".lower()
        wildlife_keywords = [
            "wildlife", "forest department", "forest dept", "forest guard", "sanctuary", "reserve", "national park",
            "tiger", "leopard", "elephant", "gaur", "wild boar", "sloth bear", "tahr", "crocodile", "macaque",
            "poaching", "animal", "rescue", "habitat", "biodiversity", "conservation", "anti-poaching", "patrol",
            "protected area", "protected forest", "human-wildlife", "human animal", "village", "crop raid", "attack",
            "trapped", "relocated", "wild animal", "forest range", "animal movement", "wildlife act",
            "வனத்துறை", "காட்டு", "விலங்கு", "புலி", "யானை", "சிறுத்தை", "காட்டுப்பன்றி", "கரடி", "ஆமை", "பராமரிப்பு"
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
            "sentiment": sentiment
        }
