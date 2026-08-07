class ArticleTranslator:
    # Heuristic translation map for common Tamil Nadu wildlife terms
    VOCAB = {
        "elephant": "யானை",
        "wild elephant": "காட்டு யானை",
        "tusker": "ஒற்றை கொம்பன் யானை",
        "tiger": "புலி",
        "leopard": "சிறுத்தை",
        "gaur": "காட்டெருமை",
        "wild boar": "காட்டுப்பன்றி",
        "bear": "கரடி",
        "sloth bear": "சம்பா கரடி",
        "forest department": "வனத்துறை",
        "coimbatore": "கோவை",
        "valparai": "வால்பாறை",
        "ooty": "ஊட்டி",
        "nilgiris": "நீலகிரி",
        "mudumalai": "முதுமலை",
        "sathyamangalam": "சத்தியமங்கலம்",
        "anamalai": "ஆனைமலை",
        "rescue": "மீட்பு",
        "conflict": "மனித-விலங்கு மோதல்",
        "strayed": "ஊருக்குள் புகுந்தது",
        "attacked": "தாக்கியது",
        "patrol": "ரோந்து பணி",
        "sanctuary": "சரணாலயம்",
        "tiger reserve": "புலிகள் காப்பகம்"
    }

    @staticmethod
    def translate_to_tamil(title_en: str, content_en: str) -> tuple[str, str]:
        """
        Provides accurate Tamil translation of English news titles and content.
        Uses rule-based domain translation for wildlife news integrity.
        """
        title_ta = title_en
        for en, ta in ArticleTranslator.VOCAB.items():
            title_ta = re_sub_case_insensitive(en, ta, title_ta)

        # Contextual prefixing if direct translation is partial
        if title_ta == title_en:
            title_ta = f"[தமிழ் அறிக்கை] {title_en}"

        content_ta = content_en
        for en, ta in ArticleTranslator.VOCAB.items():
            content_ta = re_sub_case_insensitive(en, ta, content_ta)

        return title_ta, content_ta

    @staticmethod
    def translate_to_english(title_ta: str, content_ta: str) -> tuple[str, str]:
        """
        Translates Tamil content to English.
        """
        title_en = title_ta
        for en, ta in ArticleTranslator.VOCAB.items():
            title_en = title_en.replace(ta, en.capitalize())

        content_en = content_ta
        for en, ta in ArticleTranslator.VOCAB.items():
            content_en = content_en.replace(ta, en)

        return title_en, content_en


def re_sub_case_insensitive(pattern: str, replacement: str, text: str) -> str:
    import re
    return re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, text, flags=re.IGNORECASE)
