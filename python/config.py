"""
config.py — Centralized configuration loaded from .env
"""
import os
from dotenv import load_dotenv

# Load .env file from the python/ directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Strapi
STRAPI_URL = os.getenv('STRAPI_URL', 'http://localhost:1337')
STRAPI_ADMIN_EMAIL = os.getenv('STRAPI_ADMIN_EMAIL', '')
STRAPI_ADMIN_PASSWORD = os.getenv('STRAPI_ADMIN_PASSWORD', '')
STRAPI_API_TOKEN = os.getenv('STRAPI_API_TOKEN', '')

# Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-8b-8192')

# Anime settings
ANIME_FETCH_LIMIT = int(os.getenv('ANIME_FETCH_LIMIT', '20'))

# Pollinations AI
POLLINATIONS_URL = os.getenv('POLLINATIONS_URL', 'https://image.pollinations.ai/prompt/')

# Jikan API
JIKAN_BASE_URL = 'https://api.jikan.moe/v4'
