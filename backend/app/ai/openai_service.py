import os
import json
import logging
import httpx
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

# Load .env file
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
if os.path.exists(backend_env):
    load_dotenv(backend_env)

from app.ai.classifier import ArticleClassifier
from app.ai.summarizer import ArticleSummarizer
from app.ai.translator import ArticleTranslator

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class OpenAIService:
    @staticmethod
    def process_live_article(title: str, content: str, source_name: str = "") -> Dict:
        """
        Processes a live online news article using OpenAI API if key is set,
        or falls back to local high-performance AI engine.
        Returns classified metadata, translated titles/content, and bullet summaries.
        """
        api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        if api_key:
            try:
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an AI Wildlife Intelligence Assistant for Tamil Nadu Forest Department. "
                                "Analyze the provided live online news article and return JSON with keys:\n"
                                "- title_en: Crisp title in English\n"
                                "- title_ta: Tamil translation of title\n"
                                "- content_en: Full text or clean excerpt in English\n"
                                "- content_ta: Tamil translation of main text\n"
                                "- summary_en: 3 bullet points summary in English\n"
                                "- summary_ta: 3 bullet points summary in Tamil\n"
                                "- category: Choice of ['Human-Wildlife Conflict', 'Wildlife Crime & Rescue', 'Forest Fire & Safety', 'Forest Encroachment', 'Eco-Tourism & Sanctuaries', 'Species Conservation', 'Forest Dept & Policy']\n"
                                "- conflict_level: Choice of ['High', 'Medium', 'Low', 'None']\n"
                                "- district: Tamil Nadu district name (e.g. Nilgiris, Coimbatore, Erode & Sathyamangalam, etc.)\n"
                                "- species: Array of species involved (e.g. ['Elephant', 'Tiger'])\n"
                                "- sentiment: Choice of ['Critical Alert', 'Negative', 'Positive', 'Neutral']"
                            )
                        },
                        {
                            "role": "user",
                            "content": f"Title: {title}\nContent: {content}\nSource: {source_name}"
                        }
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                response = httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=15.0
                )
                if response.status_code == 200:
                    res_json = response.json()
                    ai_content = res_json['choices'][0]['message']['content']
                    parsed = json.loads(ai_content)
                    logger.info("Successfully processed live news with OpenAI API")
                    return parsed
            except Exception as e:
                logger.warning(f"OpenAI API call failed or timed out: {e}. Falling back to Live AI Engine.")

        # Fallback to local high-performance Live AI Engine
        title_ta, content_ta = ArticleTranslator.translate_to_tamil(title, content)
        ai_meta = ArticleClassifier.classify(title, content)
        sum_en = ArticleSummarizer.summarize_en(title, content)
        sum_ta = ArticleSummarizer.summarize_ta(title_ta, content_ta)

        return {
            "title_en": title,
            "title_ta": title_ta,
            "content_en": content if content else title,
            "content_ta": content_ta if content_ta else title_ta,
            "summary_en": sum_en,
            "summary_ta": sum_ta,
            "category": ai_meta["category"],
            "conflict_level": ai_meta["conflict_level"],
            "district": ai_meta["district"],
            "species": ai_meta["species"],
            "sentiment": ai_meta["sentiment"],
            "key_entities": ai_meta["key_entities"]
        }
