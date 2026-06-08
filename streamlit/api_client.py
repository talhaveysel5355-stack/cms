"""
api_client.py — Strapi 5 uyumlu REST API istemcisi (Streamlit frontend)
Strapi 5 degisiklikleri:
  - publicationState=live  -->  status=published (veya kaldirilir)
  - Yanit formati duz obje (attributes sarmalayicisi yok)
"""
import requests
from typing import Optional

STRAPI_URL = "https://icrik-final-strapi.onrender.com"


def _get(endpoint: str, params: dict = None) -> dict:
    """Strapi'ye GET istegi yapar ve JSON doner."""
    url = f"{STRAPI_URL}/api/{endpoint}"
    try:
        response = requests.get(url, params=params or {}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        return {"error": "Strapi'ye baglanamiyorum. Strapi'nin calistigini kontrol edin: http://localhost:1337"}
    except requests.Timeout:
        return {"error": "Istek zaman asimina ugradi"}
    except requests.RequestException as e:
        # HTTP hata kodunu da goster
        msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            msg += f" | HTTP {e.response.status_code}: {e.response.text[:200]}"
        return {"error": msg}


def fetch_anime_list(
    locale: str = "tr",
    genre: Optional[str] = None,
    min_rating: float = 0.0,
    max_rating: float = 10.0,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Strapi'den anime listesini getirir.
    Strapi 5: publicationState kaldirildi, status=published kullaniliyor.
    Veri yoksa status filtresiz tekrar dener (draft girisler de gosterilir).
    """
    params = {
        "locale": locale,
        "pagination[page]": page,
        "pagination[pageSize]": page_size,
        "populate[coverImage][fields][0]": "url",
        "populate[coverImage][fields][1]": "formats",
        "fields[0]": "title",
        "fields[1]": "genre",
        "fields[2]": "rating",
        "fields[3]": "releaseYear",
        "fields[4]": "studio",
        "fields[5]": "malId",
        "sort": "rating:desc",
    }

    if genre and genre != "All":
        params["filters[genre][$eq]"] = genre

    if min_rating > 0:
        params["filters[rating][$gte]"] = min_rating

    if max_rating < 10:
        params["filters[rating][$lte]"] = max_rating

    if search:
        params["filters[title][$containsi]"] = search

    # Once yayinlanmislari dene (Strapi 5 formati)
    result = _get("animes", {**params, "status": "published"})

    # Hata varsa veya veri bos ise status filtresiz tekrar dene
    if "error" not in result:
        data = result.get("data", [])
        if not data:
            # Draft girisler dahil hepsini goster
            result = _get("animes", params)

    return result


def fetch_anime_detail(document_id: str, locale: str = "tr") -> dict:
    """
    Tek bir anime girdisini tam detaylariyla getirir.
    Strapi 5: status parametresi kullanilir.
    """
    params = {
        "locale": locale,
        "populate[coverImage][fields][0]": "url",
        "populate[coverImage][fields][1]": "formats",
        "populate[recommendations][populate][recommendedAnime][populate][coverImage][fields][0]": "url",
        "populate[recommendations][fields][0]": "recommendationReason",
        "populate[recommendations][fields][1]": "similarityScore",
    }
    result = _get(f"animes/{document_id}", {**params, "status": "published"})
    # Yayinlanmamissa draft olarak dene
    if "error" not in result and not result.get("data"):
        result = _get(f"animes/{document_id}", params)
    return result


def fetch_recommendations(anime_id: str, locale: str = "tr") -> list:
    """
    Verilen animenin kaynak oldugu onerileri getirir.
    """
    params = {
        "locale": locale,
        "filters[anime][id][$eq]": anime_id,
        "populate[recommendedAnime][populate][coverImage][fields][0]": "url",
        "fields[0]": "recommendationReason",
        "fields[1]": "similarityScore",
        "sort": "similarityScore:desc",
        "pagination[pageSize]": 6,
    }
    result = _get("recommendations", params)
    return result.get("data", [])


def check_strapi_connection() -> dict:
    """
    Strapi baglantisini ve veri varligini kontrol eder.
    Diyagnostik bilgi doner.
    """
    # Tum anime girdileri (status filtresiz)
    result = _get("animes", {"pagination[pageSize]": 1})
    if "error" in result:
        return {"ok": False, "error": result["error"], "count": 0}

    total = result.get("meta", {}).get("pagination", {}).get("total", 0)
    return {"ok": True, "count": total}


def get_image_url(image_obj: Optional[dict], prefer: str = "medium") -> Optional[str]:
    """
    Strapi medya nesnesinden en iyi gorsel URL'sini cikarir.
    """
    if not image_obj:
        return None

    base = STRAPI_URL

    # Formatlar arasinda en uygun boyutu sec
    formats = image_obj.get("formats", {}) or {}
    for size in [prefer, "medium", "small", "thumbnail", "large"]:
        if size in formats and formats[size].get("url"):
            url = formats[size]["url"]
            return url if url.startswith("http") else f"{base}{url}"

    # Dogrudan URL'ye geri don
    direct_url = image_obj.get("url")
    if direct_url:
        return direct_url if direct_url.startswith("http") else f"{base}{direct_url}"

    return None


GENRES = [
    "All",
    "Action", "Adventure", "Comedy", "Drama", "Fantasy",
    "Horror", "Mecha", "Mystery", "Romance", "Sci-Fi",
    "Slice of Life", "Sports", "Supernatural", "Thriller",
]
