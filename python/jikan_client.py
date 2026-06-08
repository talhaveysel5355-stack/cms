"""
jikan_client.py — Fetches anime data from the Jikan API (MyAnimeList)
Jikan API v4 docs: https://docs.api.jikan.moe/
"""
import time
import requests
from config import JIKAN_BASE_URL, ANIME_FETCH_LIMIT


GENRE_MAP = {
    1: 'Action',
    2: 'Adventure',
    4: 'Comedy',
    8: 'Drama',
    10: 'Fantasy',
    14: 'Horror',
    18: 'Mecha',
    7: 'Mystery',
    22: 'Romance',
    24: 'Sci-Fi',
    36: 'Slice of Life',
    30: 'Sports',
    37: 'Supernatural',
    41: 'Thriller',
}


def _map_genre(jikan_genres: list) -> str:
    """Map Jikan genre list to our enumeration. Returns the best matching genre."""
    for g in jikan_genres:
        genre_id = g.get('mal_id')
        if genre_id in GENRE_MAP:
            return GENRE_MAP[genre_id]
    return 'Action'  # default fallback


def fetch_top_anime(limit: int = ANIME_FETCH_LIMIT) -> list[dict]:
    """
    Fetch top anime from Jikan API.
    Returns list of structured anime dicts.
    """
    animes = []
    page = 1
    per_page = min(limit, 25)  # Jikan max per page is 25

    print(f"[Jikan] Fetching top {limit} anime...")

    while len(animes) < limit:
        url = f"{JIKAN_BASE_URL}/top/anime"
        params = {'page': page, 'limit': per_page}
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"[Jikan] Error fetching page {page}: {e}")
            break

        items = data.get('data', [])
        if not items:
            break

        for item in items:
            if len(animes) >= limit:
                break

            # Extract studio name
            studios = item.get('studios', [])
            studio_name = studios[0]['name'] if studios else 'Unknown'

            # Extract genre
            genres = item.get('genres', [])
            genre = _map_genre(genres)

            # Extract image URL
            images = item.get('images', {})
            image_url = images.get('jpg', {}).get('large_image_url', '')

            # Extract synopsis
            synopsis = item.get('synopsis', '') or ''

            # Extract release year
            aired = item.get('aired', {})
            from_date = aired.get('from', '')
            release_year = None
            if from_date:
                try:
                    release_year = int(from_date[:4])
                except (ValueError, TypeError):
                    release_year = None

            anime_data = {
                'mal_id': item.get('mal_id'),
                'title': item.get('title_english') or item.get('title', 'Unknown'),
                'original_title': item.get('title', ''),
                'synopsis': synopsis,
                'genre': genre,
                'studio': studio_name,
                'release_year': release_year,
                'rating': item.get('score'),
                'image_url': image_url,
                'genres_raw': [g.get('name', '') for g in genres],
            }
            animes.append(anime_data)
            print(f"[Jikan]   OK {anime_data['title']} (MAL ID: {anime_data['mal_id']})")

        page += 1
        # Respect Jikan rate limit: max 3 requests/second
        time.sleep(0.5)

    print(f"[Jikan] Fetched {len(animes)} anime total.\n")
    return animes


def fetch_anime_recommendations(mal_id: int) -> list[dict]:
    """
    Fetch recommendations for a specific anime from Jikan.
    Returns list of {mal_id, title} dicts.
    """
    url = f"{JIKAN_BASE_URL}/anime/{mal_id}/recommendations"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        recs = []
        for item in data.get('data', [])[:5]:
            entry = item.get('entry', {})
            recs.append({
                'mal_id': entry.get('mal_id'),
                'title': entry.get('title', ''),
            })
        time.sleep(0.5)
        return recs
    except requests.RequestException as e:
        print(f"[Jikan] Could not fetch recommendations for MAL ID {mal_id}: {e}")
        return []
