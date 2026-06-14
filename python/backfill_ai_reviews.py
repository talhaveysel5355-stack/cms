import time
import requests
from config import GROQ_MODEL
from ai_enricher import generate_ai_review
from strapi_client import StrapiClient

def main():
    strapi = StrapiClient()
    
    print("============================================================")
    print("  AI Review Backfill Script")
    print("============================================================")

    # Fetch all anime from Strapi
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
        
        # We need to process both TR and EN locales.
        # Fetch TR locale (default)
        tr_params = {'locale': 'tr'}
        try:
            tr_res = requests.get(f"{url}/{doc_id}", headers=strapi.headers, params=tr_params).json()
            tr_data = tr_res.get('data', {})
        except Exception:
            continue
            
        # Fetch EN locale
        en_params = {'locale': 'en'}
        try:
            en_res = requests.get(f"{url}/{doc_id}", headers=strapi.headers, params=en_params).json()
            en_data = en_res.get('data', {})
        except Exception:
            en_data = None

        print(f"\nProcessing '{title}' (ID: {doc_id})...")
        
        # Process TR
        if tr_data and not tr_data.get('aiReview'):
            print(f"  [TR] Generating review...")
            synopsis_tr = tr_data.get('synopsis', '')
            review_tr = generate_ai_review(title, synopsis_tr, language='tr')
            if review_tr:
                payload = {'data': {'aiReview': review_tr}}
                try:
                    requests.put(f"{url}/{doc_id}?locale=tr", headers=strapi.headers, json=payload)
                    print(f"  [TR] Updated successfully.")
                except Exception as e:
                    print(f"  [TR] Failed to update: {e}")
            time.sleep(1.5) # Prevent rate limits
        else:
            print("  [TR] Already has review or no data.")

        # Process EN
        if en_data and not en_data.get('aiReview'):
            print(f"  [EN] Generating review...")
            synopsis_en = en_data.get('synopsis', '')
            review_en = generate_ai_review(title, synopsis_en, language='en')
            if review_en:
                payload = {'data': {'aiReview': review_en}}
                try:
                    requests.put(f"{url}/{doc_id}?locale=en", headers=strapi.headers, json=payload)
                    print(f"  [EN] Updated successfully.")
                except Exception as e:
                    print(f"  [EN] Failed to update: {e}")
            time.sleep(1.5) # Prevent rate limits
        elif en_data:
            print("  [EN] Already has review.")
            
        # Publish again just in case
        strapi.publish_anime(doc_id)

    print("\nBackfill complete!")

if __name__ == "__main__":
    main()
