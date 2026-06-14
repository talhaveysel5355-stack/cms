import time
import requests
from config import GROQ_MODEL
from ai_enricher import generate_ai_review, translate_to_english
from strapi_client import StrapiClient

def main():
    strapi = StrapiClient()
    
    print("============================================================")
    print("  English Locale & AI Review Backfill Script")
    print("============================================================")

    url = f"{strapi.base_url}/api/animes"
    params = {
        'pagination[pageSize]': 100,
        'populate': '*'
    }
    
    try:
        response = requests.get(url, headers=strapi.headers, params=params, timeout=60)
        response.raise_for_status()
        animes = response.json().get('data', [])
    except Exception as e:
        print(f"Error fetching anime from Strapi: {e}")
        return

    print(f"Found {len(animes)} anime in Strapi.")
    
    for anime in animes:
        doc_id = anime.get('documentId')
        title = anime.get('title')
        
        # Check EN locale
        en_params = {'locale': 'en'}
        try:
            en_res = requests.get(f"{url}/{doc_id}", headers=strapi.headers, params=en_params).json()
            en_data = en_res.get('data', None)
        except Exception:
            en_data = None

        print(f"\nProcessing '{title}' (ID: {doc_id})...")
        
        if not en_data or not en_data.get('aiReview'):
            print(f"  [EN] Missing locale or aiReview. Generating...")
            
            # Use the Turkish synopsis and translate it back to English
            synopsis_tr = anime.get('synopsis', '')
            synopsis_en = translate_to_english(synopsis_tr) if synopsis_tr else ""
            
            review_en = generate_ai_review(title, synopsis_en, language='en')
            
            if review_en:
                # Add locale via strapi client
                success = strapi.add_locale_to_anime(
                    document_id=doc_id,
                    locale_data={
                        'title': title,
                        'synopsis': synopsis_en,
                        'ai_review': review_en
                    },
                    locale='en'
                )
                if success:
                    print(f"  [EN] Successfully added English locale with AI Review!")
                else:
                    print(f"  [EN] Failed to add locale via Strapi Client.")
            time.sleep(1.5) # Prevent rate limits
        else:
            print("  [EN] Already has complete English locale and review.")
            
        # Ensure it is published
        strapi.publish_anime(doc_id)

    print("\nBackfill complete!")

if __name__ == "__main__":
    main()
