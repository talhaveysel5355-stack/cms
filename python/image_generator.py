"""
image_generator.py — Generate anime-style promotional posters using Pollinations AI
Pollinations AI is a free, no-key-required image generation service.
Docs: https://pollinations.ai/
"""
import requests
import urllib.parse
from config import POLLINATIONS_URL


def generate_anime_poster(title: str, genres: list, width: int = 768, height: int = 1024) -> bytes | None:
    """
    Generate a cinematic anime poster image using Pollinations AI.
    
    Args:
        title: Anime title for the prompt
        genres: List of genre strings to include in the prompt
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        Image bytes if successful, None on failure
    """
    genre_str = ', '.join(genres[:3]) if genres else 'fantasy adventure'
    
    prompt = (
        f"cinematic anime poster for '{title}', {genre_str} style, "
        "vibrant colors, high detail, dramatic lighting, "
        "professional anime artwork, Studio Ghibli quality, "
        "epic composition, atmospheric, 4K resolution"
    )
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_URL}{encoded_prompt}?width={width}&height={height}&nologo=true&seed={hash(title) % 9999}"
    
    print(f"[Image] Generating poster for '{title}'...")
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Verify it's actually an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type and len(response.content) < 1000:
            print(f"[Image] ERR Invalid response for '{title}' (content-type: {content_type})")
            return None
        
        print(f"[Image] OK Generated poster for '{title}' ({len(response.content)} bytes)")
        return response.content
        
    except requests.Timeout:
        print(f"[Image] ERR Timeout generating poster for '{title}'")
        return None
    except requests.RequestException as e:
        print(f"[Image] ERR Error generating poster for '{title}': {e}")
        return None


def download_image_from_url(url: str) -> bytes | None:
    """
    Download an existing image from a URL (e.g., Jikan cover images).
    
    Args:
        url: Direct image URL
    
    Returns:
        Image bytes if successful, None on failure
    """
    if not url:
        return None
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"[Image] Could not download from {url}: {e}")
        return None
