"""
strapi_client.py — Strapi CMS REST API client with JWT authentication
Handles: authentication, image upload, anime CRUD, recommendation CRUD
"""
import io
import requests
from config import STRAPI_URL, STRAPI_ADMIN_EMAIL, STRAPI_ADMIN_PASSWORD, STRAPI_API_TOKEN


class StrapiClient:
    """
    Client for interacting with the Strapi CMS REST API.
    Authenticates with admin credentials and stores the JWT token.
    """

    def __init__(self):
        self.base_url = STRAPI_URL.rstrip('/')
        self.token: str | None = None
        self.headers: dict = {'Content-Type': 'application/json'}

        # Eger API Token varsa, dogrudan kullan (giris gerekmez)
        if STRAPI_API_TOKEN:
            self.token = STRAPI_API_TOKEN
            self.headers = {
                'Authorization': f'Bearer {STRAPI_API_TOKEN}',
                'Content-Type': 'application/json'
            }

    # ------------------------------------------------------------------ #
    # Authentication
    # ------------------------------------------------------------------ #

    def login(self) -> bool:
        """
        Strapi'ye giris yapar.
        1. Oncelikle API Token kullanir (varsa aninda dogrular)
        2. Yoksa /api/auth/local ile email/sifre ile giris yapar
        """
        # API Token zaten yuklendi mi?
        if STRAPI_API_TOKEN:
            # Token'in calismali oldugunu dogrula
            test_url = f"{self.base_url}/api/animes?pagination[pageSize]=1"
            try:
                r = requests.get(test_url, headers=self.headers, timeout=10)
                if r.status_code == 200:
                    print(f"[Strapi] OK API Token ile dogrulama basarili")
                    return True
                else:
                    print(f"[Strapi] ERR API Token gecersiz: HTTP {r.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"[Strapi] ERR Strapi'ye baglanilemiyor: {e}")
                return False

        # API Token yoksa email/sifre ile giris dene
        if not STRAPI_ADMIN_EMAIL or not STRAPI_ADMIN_PASSWORD:
            print("[Strapi] ERR Ne API Token ne de email/sifre ayarli. python/.env dosyasini kontrol edin.")
            return False

        url = f"{self.base_url}/api/auth/local"
        payload = {
            'identifier': STRAPI_ADMIN_EMAIL,
            'password': STRAPI_ADMIN_PASSWORD
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            self.token = data.get('jwt')
            if self.token:
                self.headers = {
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
                print(f"[Strapi] OK Giris basarili: {STRAPI_ADMIN_EMAIL}")
                return True
            print("[Strapi] ERR Yanit icinde JWT bulunamadi")
            return False
        except requests.RequestException as e:
            print(f"[Strapi] ERR Giris basarisiz: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"         Yanit: {e.response.text[:200]}")
            return False

    # ------------------------------------------------------------------ #
    # Media Upload
    # ------------------------------------------------------------------ #

    def upload_image(self, image_bytes: bytes, filename: str, ref_id: int | None = None,
                     ref: str | None = None, field: str | None = None) -> int | None:
        """
        Upload an image to Strapi Media Library.
        
        Args:
            image_bytes: Raw image bytes
            filename: Filename with extension (e.g., 'naruto_poster.jpg')
            ref_id: Optional — Strapi entry ID to link this image to
            ref: Optional — content-type API ID (e.g., 'api::anime.anime')
            field: Optional — field name to attach to (e.g., 'coverImage')
        
        Returns:
            Uploaded file ID, or None on failure
        """
        url = f"{self.base_url}/api/upload"
        
        # Auth headers without Content-Type (multipart sets its own)
        headers = {'Authorization': f'Bearer {self.token}'}
        
        files = {
            'files': (filename, io.BytesIO(image_bytes), 'image/jpeg')
        }
        data = {}
        if ref_id:
            data['refId'] = str(ref_id)
        if ref:
            data['ref'] = ref
        if field:
            data['field'] = field

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            file_id = result[0].get('id') if isinstance(result, list) else result.get('id')
            print(f"[Strapi] OK Uploaded image '{filename}' -> ID {file_id}")
            return file_id
        except requests.RequestException as e:
            print(f"[Strapi] ERR Image upload failed for '{filename}': {e}")
            return None

    # ------------------------------------------------------------------ #
    # Anime CRUD
    # ------------------------------------------------------------------ #

    def get_all_anime(self) -> list[dict]:
        """Fetch all anime entries (for deduplication by malId)."""
        url = f"{self.base_url}/api/animes"
        params = {'pagination[pageSize]': 100, 'fields[0]': 'malId', 'fields[1]': 'title'}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.RequestException as e:
            print(f"[Strapi] ERR Could not fetch anime list: {e}")
            return []

    def get_existing_mal_ids(self) -> set[int]:
        """Return a set of all MAL IDs already stored in Strapi."""
        anime_list = self.get_all_anime()
        mal_ids = set()
        for entry in anime_list:
            mal_id = entry.get('malId') or entry.get('attributes', {}).get('malId')
            if mal_id:
                mal_ids.add(int(mal_id))
        return mal_ids

    def create_anime(self, anime_data: dict, locale: str = 'tr') -> int | None:
        """
        Create a new Anime entry in Strapi.
        
        Args:
            anime_data: Dict with all anime fields
            locale: Content locale ('tr' or 'en')
        
        Returns:
            Created entry document ID, or None on failure
        """
        url = f"{self.base_url}/api/animes"
        payload = {
            'data': {
                'title': anime_data.get('title', ''),
                'originalTitle': anime_data.get('original_title', ''),
                'synopsis': anime_data.get('synopsis', ''),
                'genre': anime_data.get('genre', 'Action'),
                'studio': anime_data.get('studio', ''),
                'releaseYear': anime_data.get('release_year'),
                'rating': anime_data.get('rating'),
                'malId': anime_data.get('mal_id'),
                'locale': locale,
            }
        }
        # Attach cover image if available
        if anime_data.get('cover_image_id'):
            payload['data']['coverImage'] = anime_data['cover_image_id']

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            entry = result.get('data', {})
            # Strapi 5: documentId (string) kullan, numerik id degil
            entry_id = entry.get('documentId') or entry.get('id')
            print(f"[Strapi] OK Created anime '{anime_data.get('title')}' -> ID {entry_id}")
            return entry_id
        except requests.RequestException as e:
            print(f"[Strapi] ERR Failed to create anime '{anime_data.get('title')}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"         Response: {e.response.text[:300]}")
            return None

    def add_locale_to_anime(self, document_id, locale_data: dict, locale: str) -> bool:
        """
        Add a localized version (e.g., English) to an existing Anime entry.
        Strapi 5: PUT /api/animes/{documentId} with ?locale= query param
        """
        url = f"{self.base_url}/api/animes/{document_id}"
        payload = {
            'data': {
                'title': locale_data.get('title', ''),
                'synopsis': locale_data.get('synopsis', ''),
            }
        }
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=payload,
                params={'locale': locale},
                timeout=15
            )
            response.raise_for_status()
            print(f"[Strapi] OK Added {locale} locale for anime ID {document_id}")
            return True
        except requests.RequestException as e:
            # Locale eklenemezse sessizce devam et (ana kayit tamam)
            print(f"[Strapi] WARN {locale} locale eklenemedi (ID {document_id}): {e}")
            return False

    def publish_anime(self, document_id) -> bool:
        """Publish an anime entry."""
        url = f"{self.base_url}/api/animes/{document_id}"
        payload = {'data': {'publishedAt': 'now'}}
        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------ #
    # Recommendation CRUD
    # ------------------------------------------------------------------ #

    def create_recommendation(self, source_anime_id, target_anime_id,
                               reason_tr: str, reason_en: str,
                               similarity_score: float) -> int | None:
        """
        Create a Recommendation entry linking two anime entries.
        
        Args:
            source_anime_id: Strapi document ID of the source anime
            target_anime_id: Strapi document ID of the recommended anime
            reason_tr: Turkish recommendation explanation
            reason_en: English recommendation explanation
            similarity_score: Float between 0–1
        
        Returns:
            Created recommendation document ID, or None on failure
        """
        url = f"{self.base_url}/api/recommendations"
        payload = {
            'data': {
                'recommendationReason': reason_tr,
                'similarityScore': similarity_score,
                'anime': source_anime_id,
                'recommendedAnime': target_anime_id,
                'locale': 'tr',
            }
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            entry = result.get('data', {})
            entry_id = entry.get('id') or entry.get('documentId')
            print(f"[Strapi] OK Created recommendation ID {entry_id}")
            return entry_id
        except requests.RequestException as e:
            print(f"[Strapi] ERR Failed to create recommendation: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"         Response: {e.response.text[:300]}")
            return None
