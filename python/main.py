"""
main.py — Orchestrator for the Anime Recommendation Automation Engine

Pipeline:
1. Authenticate with Strapi
2. Fetch top anime from Jikan (MyAnimeList)
3. For each anime:
   a. Translate synopsis to Turkish
   b. Expand synopsis with AI
   c. Generate AI poster via Pollinations
   d. Download original cover image
   e. Upload images to Strapi
   f. Create Anime entry (TR locale)
   g. Add English locale version
4. Generate AI-powered recommendations between similar anime
5. Save recommendations to Strapi

Usage:
    python main.py              # Full run
    python main.py --dry-run    # Test pipeline without saving to Strapi
    python main.py --skip-images # Skip image generation (faster)
    python main.py --limit 5    # Process only 5 anime
"""
import sys
import time
import argparse

# Windows konsolunda UTF-8 karakterleri dogru gostermek icin
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import ANIME_FETCH_LIMIT
from jikan_client import fetch_top_anime
from ai_enricher import (
    translate_to_turkish, translate_to_english,
    expand_synopsis, generate_recommendation_reason,
    compute_similarity_score
)
from image_generator import generate_anime_poster, download_image_from_url
from strapi_client import StrapiClient


def parse_args():
    parser = argparse.ArgumentParser(description='Anime Recommendation Automation Engine')
    parser.add_argument('--dry-run', action='store_true',
                        help='Run pipeline without saving to Strapi')
    parser.add_argument('--skip-images', action='store_true',
                        help='Skip AI poster generation (faster)')
    parser.add_argument('--skip-ai', action='store_true',
                        help='Skip AI enrichment (use original synopsis)')
    parser.add_argument('--limit', type=int, default=ANIME_FETCH_LIMIT,
                        help=f'Number of anime to process (default: {ANIME_FETCH_LIMIT})')
    return parser.parse_args()


def process_anime(anime: dict, strapi: StrapiClient, args, existing_ids: set) -> dict | None:
    """
    Process a single anime entry through the full pipeline.
    Returns the processed anime dict with Strapi ID, or None if skipped.
    """
    mal_id = anime.get('mal_id')
    title = anime.get('title', 'Unknown')

    # Skip already-stored anime
    if mal_id and mal_id in existing_ids:
        print(f"[Main] Skipping '{title}' — already in Strapi (MAL ID: {mal_id})")
        return None

    print(f"\n[Main] Processing: {title}")
    print("-" * 60)

    # Step A: Translate synopsis
    original_synopsis = anime.get('synopsis', '')
    synopsis_tr = original_synopsis  # Jikan provides English — translate to Turkish
    synopsis_en = original_synopsis

    if not args.skip_ai and original_synopsis:
        # Translate English -> Turkish
        synopsis_tr = translate_to_turkish(original_synopsis)
        # Expand Turkish synopsis with AI
        synopsis_tr = expand_synopsis(title, synopsis_tr, language='tr')
        # Expand English synopsis with AI
        synopsis_en = expand_synopsis(title, original_synopsis, language='en')
    elif original_synopsis:
        synopsis_tr = translate_to_turkish(original_synopsis)

    # Step B: Download original cover image
    cover_image_id = None
    ai_poster_id = None
    genres = anime.get('genres_raw', [anime.get('genre', '')])

    if not args.skip_images and not args.dry_run:
        # Download existing cover from MyAnimeList
        cover_bytes = download_image_from_url(anime.get('image_url', ''))
        if cover_bytes:
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-')).strip()[:30]
            cover_image_id = strapi.upload_image(
                cover_bytes,
                f"{safe_title}_cover.jpg"
            )

        # Generate AI poster via Pollinations
        poster_bytes = generate_anime_poster(title, genres)
        if poster_bytes:
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-')).strip()[:30]
            ai_poster_id = strapi.upload_image(
                poster_bytes,
                f"{safe_title}_ai_poster.jpg"
            )

    # Step C: Create Strapi entry
    anime_entry_data = {
        **anime,
        'synopsis': synopsis_tr,
        'cover_image_id': cover_image_id or ai_poster_id,
    }

    strapi_id = None
    if not args.dry_run:
        strapi_id = strapi.create_anime(anime_entry_data, locale='tr')

        if strapi_id:
            # Add English locale
            strapi.add_locale_to_anime(
                strapi_id,
                {'title': title, 'synopsis': synopsis_en},
                locale='en'
            )
            # Publish the entry
            strapi.publish_anime(strapi_id)
            existing_ids.add(mal_id)
    else:
        print(f"[DryRun] Would create anime: {title}")
        print(f"[DryRun] TR Synopsis preview: {synopsis_tr[:150]}...")
        strapi_id = mal_id  # Use MAL ID as fake Strapi ID for dry run

    return {
        **anime,
        'strapi_id': strapi_id,
        'synopsis_tr': synopsis_tr,
        'synopsis_en': synopsis_en,
        'genres_raw': genres,
    }


def generate_recommendations(processed_anime: list[dict], strapi: StrapiClient, args):
    """
    For each anime, find top 3 similar anime by genre overlap and generate recommendations.
    """
    print(f"\n[Main] Generating recommendations for {len(processed_anime)} anime...")
    print("=" * 60)

    recommendation_count = 0

    for i, source in enumerate(processed_anime):
        source_id = source.get('strapi_id')
        source_title = source.get('title', '')
        source_genres = source.get('genres_raw', [source.get('genre', '')])

        # Find top 3 similar anime (excluding self)
        similarities = []
        for j, target in enumerate(processed_anime):
            if i == j:
                continue
            target_genres = target.get('genres_raw', [target.get('genre', '')])
            score = compute_similarity_score(source_genres, target_genres)
            if score > 0:
                similarities.append((score, target))

        # Sort by similarity score descending, take top 3
        top_similar = sorted(similarities, key=lambda x: x[0], reverse=True)[:3]

        for score, target in top_similar:
            target_id = target.get('strapi_id')
            target_title = target.get('title', '')
            target_genres = target.get('genres_raw', [target.get('genre', '')])

            # Generate AI recommendation reason (Turkish)
            reason_tr = generate_recommendation_reason(
                source_title, target_title,
                source_genres, target_genres,
                language='tr'
            )
            # Generate English version
            reason_en = generate_recommendation_reason(
                source_title, target_title,
                source_genres, target_genres,
                language='en'
            )

            if args.dry_run:
                print(f"[DryRun] Recommendation: '{source_title}' -> '{target_title}'")
                print(f"         Score: {score}, Reason: {reason_tr[:80]}...")
            else:
                strapi.create_recommendation(
                    source_anime_id=source_id,
                    target_anime_id=target_id,
                    reason_tr=reason_tr,
                    reason_en=reason_en,
                    similarity_score=score
                )

            recommendation_count += 1
            # Small delay to avoid rate limiting OpenAI
            time.sleep(0.3)

    print(f"\n[Main] >> Created {recommendation_count} recommendations total.")


def main():
    args = parse_args()

    print("=" * 60)
    print("  Anime Recommendation Automation Engine")
    print("  AI-Powered Multilingual Discovery System")
    print("=" * 60)

    if args.dry_run:
        print(">>> DRY RUN MODE — No data will be saved to Strapi <<<\n")

    # Step 1: Initialize Strapi client
    strapi = StrapiClient()
    existing_ids = set()

    if not args.dry_run:
        if not strapi.login():
            print("[Main] ERROR: Cannot connect to Strapi. Check credentials in .env")
            print("[Main] Make sure Strapi is running at http://localhost:1337")
            sys.exit(1)
        existing_ids = strapi.get_existing_mal_ids()
        print(f"[Main] Found {len(existing_ids)} existing anime in Strapi\n")

    # Step 2: Fetch anime from Jikan
    anime_list = fetch_top_anime(limit=args.limit)
    if not anime_list:
        print("[Main] ERROR: No anime fetched from Jikan API")
        sys.exit(1)

    # Step 3: Process each anime
    processed = []
    for anime in anime_list:
        result = process_anime(anime, strapi, args, existing_ids)
        if result:
            processed.append(result)
        # Rate limit: Jikan allows 3 req/sec
        time.sleep(0.5)

    print(f"\n[Main] >> Processed {len(processed)} anime successfully")

    # Step 4: Generate recommendations
    if processed:
        generate_recommendations(processed, strapi, args)

    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print(f"  Anime processed: {len(processed)}")
    print(f"  Strapi URL: {strapi.base_url}/admin")
    print("=" * 60)


if __name__ == '__main__':
    main()
