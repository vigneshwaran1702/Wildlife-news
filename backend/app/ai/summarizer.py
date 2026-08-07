import re

class ArticleSummarizer:
    @staticmethod
    def summarize_en(title: str, content: str) -> str:
        """
        Generates a crisp 3-bullet point executive summary in English.
        """
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

        if not sentences:
            return f"• {title}\n• Detailed report on wildlife activity in Tamil Nadu.\n• Forest department teams are monitoring the situation."

        bullet_1 = f"• {sentences[0]}"
        bullet_2 = f"• {sentences[1]}" if len(sentences) > 1 else f"• Forest Department and local authorities dispatched teams for ground surveillance."
        bullet_3 = f"• {sentences[2]}" if len(sentences) > 2 else f"• Local residents urged to follow forest advisory safety guidelines."

        return f"{bullet_1}\n{bullet_2}\n{bullet_3}"

    @staticmethod
    def summarize_ta(title_ta: str, content_ta: str) -> str:
        """
        Generates a crisp 3-bullet point executive summary in Tamil.
        """
        if not content_ta:
            return f"• {title_ta or 'வனவிலங்கு பற்றிய முக்கிய செய்தி'}\n• தமிழ்நாடு வனத்துறை அதிகாரிகளின் கண்காணிப்பு பணி தொடர்கிறது.\n• பொதுமக்கள் எச்சரிக்கையுடன் இருக்குமாறு கேட்டுக்கொள்ளப்படுகிறார்கள்."

        sentences = re.split(r'(?<=[.!?।])\s+', content_ta.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return f"• {title_ta}\n• வனவிலங்கு நகர்வுகள் மற்றும் வனத்துறை நடவடிக்கைகள்.\n• மக்கள் பாதுகாப்பு நெறிமுறைகளை பின்பற்றுமாறு கேட்டுக்கொள்ளப்படுகிறார்கள்."

        b1 = f"• {sentences[0]}"
        b2 = f"• {sentences[1]}" if len(sentences) > 1 else "• வனத்துறை மற்றும் சிறப்பு மீட்புக் குழுக்கள் தீவிர கண்காணிப்பில் ஈடுபட்டுள்ளன."
        b3 = f"• {sentences[2]}" if len(sentences) > 2 else "• கிராம மக்கள் இரவு நேரத்தில் வனப் எல்லை பகுதிக்கு செல்வதைத் தவிர்க்க அறிவுறுத்தப்பட்டுள்ளனர்."

        return f"{b1}\n{b2}\n{b3}"
