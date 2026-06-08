"""
components.py — Reusable Streamlit UI components for the Anime Discovery System
"""
import streamlit as st
from api_client import get_image_url


# ─────────────────────────────────────────────────────────────────────────────
# Labels (TR / EN)
# ─────────────────────────────────────────────────────────────────────────────

LABELS = {
    "tr": {
        "rating": "Puan",
        "genre": "Tür",
        "studio": "Stüdyo",
        "year": "Yıl",
        "synopsis": "Özet",
        "recommendations": "Önerilen Animeler",
        "similarity": "Benzerlik",
        "why": "Neden Önerildi?",
        "no_synopsis": "Özet mevcut değil.",
        "no_recs": "Henüz öneri bulunmuyor.",
        "back": "← Listeye Dön",
        "detail": "Detayları Gör →",
        "no_image": "Görsel Yok",
        "ai_poster": "🎨 AI Posteri",
        "score": "Puan",
    },
    "en": {
        "rating": "Rating",
        "genre": "Genre",
        "studio": "Studio",
        "year": "Year",
        "synopsis": "Synopsis",
        "recommendations": "Recommended Anime",
        "similarity": "Similarity",
        "why": "Why Recommended?",
        "no_synopsis": "No synopsis available.",
        "no_recs": "No recommendations yet.",
        "back": "← Back to List",
        "detail": "View Details →",
        "no_image": "No Image",
        "ai_poster": "🎨 AI Poster",
        "score": "Score",
    },
}


def lbl(key: str, locale: str = "tr") -> str:
    """Return a label string for the given key and locale."""
    return LABELS.get(locale, LABELS["tr"]).get(key, key)


# ─────────────────────────────────────────────────────────────────────────────
# Genre Badge Colors
# ─────────────────────────────────────────────────────────────────────────────

GENRE_COLORS = {
    "Action": "#e63946",
    "Adventure": "#f4a261",
    "Comedy": "#2ec4b6",
    "Drama": "#9b5de5",
    "Fantasy": "#4361ee",
    "Horror": "#7b2d00",
    "Mecha": "#457b9d",
    "Mystery": "#6d6875",
    "Romance": "#e07a90",
    "Sci-Fi": "#0077b6",
    "Slice of Life": "#52b788",
    "Sports": "#f77f00",
    "Supernatural": "#7400b8",
    "Thriller": "#b5179e",
}


def genre_badge(genre: str) -> str:
    """Return an HTML span badge for a genre."""
    color = GENRE_COLORS.get(genre, "#6c757d")
    return (
        f'<span style="background:{color};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.75rem;font-weight:600;'
        f'letter-spacing:0.5px;margin-right:4px;">{genre}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Rating Stars
# ─────────────────────────────────────────────────────────────────────────────

def rating_stars(rating: float) -> str:
    """Return a colored rating badge with star icon."""
    if not rating:
        return '<span style="color:#888;">N/A</span>'
    color = "#f4c430" if rating >= 8 else "#f4a261" if rating >= 6 else "#e63946"
    return (
        f'<span style="color:{color};font-weight:700;font-size:0.9rem;">'
        f'⭐ {rating:.1f}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Anime Card Component
# ─────────────────────────────────────────────────────────────────────────────

def anime_card(anime: dict, locale: str = "tr", key_prefix: str = "") -> bool:
    """
    Render an anime card in a dark glassmorphism style.
    Returns True if the user clicked "View Details".
    
    Args:
        anime: Strapi anime entry dict
        locale: Current locale
        key_prefix: Unique prefix for button keys
    
    Returns:
        True if detail button was clicked
    """
    title = anime.get("title", "Unknown")
    genre = anime.get("genre", "")
    rating = anime.get("rating")
    year = anime.get("releaseYear", "")
    studio = anime.get("studio", "")
    cover_image = anime.get("coverImage")
    image_url = get_image_url(cover_image, prefer="small") if cover_image else None

    clicked = False

    with st.container():
        # Card HTML wrapper
        st.markdown(
            f"""
            <div class="anime-card">
                <div class="card-image-container">
            """,
            unsafe_allow_html=True,
        )

        # Cover Image
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.markdown(
                f'<div class="no-image-placeholder">🎌 {lbl("no_image", locale)}</div>',
                unsafe_allow_html=True,
            )

        # Card content
        st.markdown(
            f"""
                </div>
                <div class="card-content">
                    <h3 class="card-title">{title}</h3>
                    <div class="card-meta">
                        {genre_badge(genre)}
                    </div>
                    <div class="card-stats">
                        {rating_stars(rating)}
                        <span class="card-year">{year}</span>
                    </div>
                    <div class="card-studio">{studio}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Detail button
        entry_id = anime.get("id") or anime.get("documentId")
        btn_key = f"{key_prefix}_detail_{entry_id}"
        if st.button(lbl("detail", locale), key=btn_key, use_container_width=True):
            clicked = True

    return clicked


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Card
# ─────────────────────────────────────────────────────────────────────────────

def recommendation_card(rec: dict, locale: str = "tr", key_prefix: str = "") -> str | None:
    """
    Render a recommendation card showing the recommended anime and AI reason.
    Returns the document ID of the recommended anime if the user clicks it, else None.
    
    Args:
        rec: Strapi recommendation entry dict
        locale: Current locale
        key_prefix: Unique prefix for button keys
    
    Returns:
        Document ID string if user clicks to navigate, None otherwise
    """
    reason = rec.get("recommendationReason", "")
    score = rec.get("similarityScore", 0.0)
    rec_anime = rec.get("recommendedAnime", {}) or {}

    if not rec_anime:
        return None

    title = rec_anime.get("title", "Unknown")
    genre = rec_anime.get("genre", "")
    rating = rec_anime.get("rating")
    cover = rec_anime.get("coverImage")
    image_url = get_image_url(cover, prefer="thumbnail") if cover else None

    clicked_id = None
    score_pct = int((score or 0) * 100)

    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            if image_url:
                st.image(image_url, use_container_width=True)
            else:
                st.markdown(
                    '<div class="rec-no-image">🎌</div>',
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown(
                f"""
                <div class="rec-content">
                    <div class="rec-title">{title}</div>
                    <div class="rec-badges">
                        {genre_badge(genre)}
                        {rating_stars(rating)}
                    </div>
                    <div class="rec-score-bar">
                        <span class="rec-score-label">{lbl("similarity", locale)}: {score_pct}%</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:{score_pct}%"></div>
                        </div>
                    </div>
                    <div class="rec-reason">
                        <span class="rec-why-label">💡 {lbl("why", locale)}</span>
                        <p>{reason}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            rec_id = rec_anime.get("id") or rec_anime.get("documentId")
            if st.button(lbl("detail", locale), key=f"{key_prefix}_rec_{rec_id}", use_container_width=True):
                clicked_id = str(rec_id)

    st.markdown("---")
    return clicked_id


# ─────────────────────────────────────────────────────────────────────────────
# Strapi Connection Error Banner
# ─────────────────────────────────────────────────────────────────────────────

def connection_error_banner(locale: str = "tr"):
    """Show a styled error banner when Strapi is unreachable."""
    if locale == "tr":
        st.error(
            "⚠️ **Strapi'ye bağlanılamıyor**\n\n"
            "Render ücretsiz sunucusu **uyku moduna** geçmiş olabilir. Sunucunun uyanması ~50 saniye sürebilir, lütfen sayfayı yenileyin.\n\n"
            "Eğer veri yoksa Python scriptini çalıştırarak veri ekleyin: `python main.py`"
        )
    else:
        st.error(
            "⚠️ **Cannot connect to Strapi**\n\n"
            "The Render free tier server might be **asleep**. It can take ~50 seconds to wake up, please refresh the page.\n\n"
            "If it's empty, run the Python script to fetch data: `python main.py`"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Loading Spinner
# ─────────────────────────────────────────────────────────────────────────────

def loading_spinner(locale: str = "tr"):
    text = "Animeler yükleniyor..." if locale == "tr" else "Loading anime..."
    return st.spinner(text)
