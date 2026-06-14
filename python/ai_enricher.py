"""
ai_enricher.py — AI-powered content enrichment
Uses OpenAI for text generation and deep-translator for translation
"""
import time
from deep_translator import GoogleTranslator
from config import GROQ_API_KEY, GROQ_MODEL

# Groq client — lazily initialized only when API key is available
_groq_client = None

def _get_client():
    """Return a cached Groq client, or None if no API key is configured."""
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            return None
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def translate_to_turkish(text: str) -> str:
    """Translate English text to Turkish using Google Translate."""
    if not text or len(text.strip()) < 5:
        return text
    try:
        translated = GoogleTranslator(source='en', target='tr').translate(text)
        return translated or text
    except Exception as e:
        print(f"[Translator] Translation error: {e}")
        return text


def translate_to_english(text: str) -> str:
    """Translate Turkish text to English using Google Translate."""
    if not text or len(text.strip()) < 5:
        return text
    try:
        translated = GoogleTranslator(source='tr', target='en').translate(text)
        return translated or text
    except Exception as e:
        print(f"[Translator] Translation error: {e}")
        return text


def expand_synopsis(title: str, synopsis: str, language: str = 'tr') -> str:
    """
    Use OpenAI to expand a short anime synopsis into a detailed 3-paragraph summary.
    Returns the expanded synopsis in the requested language.
    """
    client = _get_client()
    if not client:
        print("[AI] Groq anahtarı yok — orijinal özet kullanılıyor.")
        return synopsis

    lang_instruction = "in Turkish" if language == 'tr' else "in English"
    
    prompt = f"""You are an anime expert writer. Given the following anime title and short synopsis, 
write a detailed, engaging 3-paragraph summary {lang_instruction} that covers:
1. The main story premise and setting
2. The key characters and their motivations  
3. What makes this anime unique and worth watching

Anime Title: {title}
Original Synopsis: {synopsis}

Write only the expanded synopsis, no headers or labels. Keep it engaging and spoiler-free."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert anime content writer who creates detailed, engaging anime descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        expanded = response.choices[0].message.content.strip()
        print(f"[AI] OK Expanded synopsis for '{title}' ({len(expanded)} chars)")
        return expanded
    except Exception as e:
        print(f"[AI] Groq error for '{title}': {e}")
        return synopsis


def generate_recommendation_reason(source_title: str, target_title: str, 
                                    source_genres: list, target_genres: list,
                                    language: str = 'tr') -> str:
    """
    Generate an AI explanation for why target_title is recommended to fans of source_title.
    Returns explanation text in the requested language.
    """
    client = _get_client()
    if not client:
        common_genres = set(source_genres) & set(target_genres)
        shared_str = ', '.join(common_genres) if common_genres else 'benzer temalar'
        return (f"Önerilir çünkü '{source_title}' ile {shared_str} paylaşmaktadır."
                if language == 'tr'
                else f"Recommended because it shares {shared_str} with {source_title}.")

    lang_instruction = "in Turkish" if language == 'tr' else "in English"
    shared = list(set(source_genres) & set(target_genres))

    prompt = f"""Write a single compelling sentence (max 40 words) {lang_instruction} explaining why 
someone who loves "{source_title}" would also enjoy "{target_title}".

Source anime genres: {', '.join(source_genres)}
Target anime genres: {', '.join(target_genres)}
Shared themes/genres: {', '.join(shared) if shared else 'similar storytelling style'}

Start the sentence with "Recommended because..." or the Turkish equivalent "Önerilir çünkü..."
Write only the recommendation sentence, nothing else."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an anime recommendation expert who creates concise, insightful recommendation explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.8
        )
        reason = response.choices[0].message.content.strip()
        print(f"[AI] OK Recommendation: '{source_title}' -> '{target_title}'")
        return reason
    except Exception as e:
        print(f"[AI] Recommendation error: {e}")
        shared_str = ', '.join(shared) if shared else 'similar themes'
        return f"Önerilir çünkü '{source_title}' ile benzer {shared_str} özelliklerini paylaşmaktadır." if language == 'tr' \
               else f"Recommended because it shares {shared_str} with {source_title}."


def compute_similarity_score(genres_a: list, genres_b: list) -> float:
    """Compute a simple Jaccard similarity score between two genre lists."""
    if not genres_a or not genres_b:
        return 0.0
    set_a = set(genres_a)
    set_b = set(genres_b)
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return round(intersection / union, 2) if union > 0 else 0.0
