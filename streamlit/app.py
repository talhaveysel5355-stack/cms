"""
app.py — Streamlit Frontend: AI-Powered Multilingual Anime Discovery System

Run with:
    streamlit run app.py

Features:
- Dark anime-streaming-platform theme
- Language switch (TR / EN)
- Genre & rating filters
- Full-text search
- Anime grid with card layout
- Detail page with synopsis, AI poster, recommendations
- AI-generated recommendation explanations with similarity scores
"""

import streamlit as st
from api_client import fetch_anime_list, fetch_anime_detail, fetch_recommendations, get_image_url, GENRES, check_strapi_connection
from components import (
    anime_card, recommendation_card, connection_error_banner,
    loading_spinner, lbl, genre_badge, rating_stars
)

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AnimeAI — AI Destekli Anime Keşif",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS — Dark Anime Theme
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a2e;
    --bg-card-hover: #16213e;
    --accent: #6c63ff;
    --accent2: #e040fb;
    --accent-gradient: linear-gradient(135deg, #6c63ff, #e040fb);
    --text-primary: #f0f0f5;
    --text-secondary: #9090a0;
    --text-muted: #606070;
    --border: rgba(108, 99, 255, 0.2);
    --glow: 0 0 20px rgba(108, 99, 255, 0.3);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: radial-gradient(ellipse at 20% 0%, rgba(108, 99, 255, 0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 100%, rgba(224, 64, 251, 0.06) 0%, transparent 60%),
                var(--bg-primary) !important;
    min-height: 100vh;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary) !important;
}

/* ── Header Banner ── */
.app-header {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0d2e 50%, #0d1a2e 100%);
    border-bottom: 2px solid transparent;
    border-image: var(--accent-gradient) 1;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(108, 99, 255, 0.05) 0%, transparent 60%);
    animation: pulse 6s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}
.app-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}
.app-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Search Bar ── */
.stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}

/* ── Selectbox & Slider ── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}
.stSlider [data-testid="stSlider"] { accent-color: var(--accent) !important; }

/* ── Anime Card ── */
.anime-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 0.5rem;
    position: relative;
}
.anime-card:hover {
    border-color: var(--accent);
    box-shadow: var(--glow), 0 12px 40px rgba(0,0,0,0.5);
    transform: translateY(-4px);
}
.card-image-container img {
    width: 100%;
    height: 240px;
    object-fit: cover;
    border-radius: 12px 12px 0 0;
}
.no-image-placeholder {
    height: 240px;
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-size: 1rem;
    border-radius: 12px 12px 0 0;
}
.card-content {
    padding: 0.9rem;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card-meta { margin-bottom: 0.4rem; }
.card-stats {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 0.4rem;
}
.card-year {
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 500;
}
.card-studio {
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-top: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Detail Page ── */
.detail-header {
    background: linear-gradient(135deg, var(--bg-card), #0f0f1f);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.detail-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(108, 99, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.detail-title {
    font-size: 2rem;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}
.detail-original-title {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 1rem;
    font-style: italic;
}
.detail-stats-row {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin: 1rem 0;
}
.stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.stat-label {
    color: var(--text-muted);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}
.stat-value {
    color: var(--text-primary);
    font-size: 0.95rem;
    font-weight: 600;
}

/* ── Synopsis ── */
.synopsis-box {
    background: rgba(108, 99, 255, 0.05);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 1.5rem 0;
    color: var(--text-primary);
    line-height: 1.8;
    font-size: 0.95rem;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid transparent;
    border-image: var(--accent-gradient) 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Recommendation Card ── */
.rec-content {
    padding: 0.5rem 0;
}
.rec-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}
.rec-badges {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.6rem;
}
.rec-score-bar { margin-bottom: 0.6rem; }
.rec-score-label {
    color: var(--text-secondary);
    font-size: 0.75rem;
    display: block;
    margin-bottom: 0.3rem;
}
.progress-bar {
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: var(--accent-gradient);
    border-radius: 4px;
    transition: width 0.6s ease;
}
.rec-reason {
    background: rgba(108, 99, 255, 0.08);
    border-radius: 8px;
    padding: 0.7rem;
    margin-top: 0.5rem;
}
.rec-why-label {
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: block;
    margin-bottom: 0.3rem;
}
.rec-reason p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.5;
}
.rec-no-image {
    height: 80px;
    background: var(--bg-card);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    border-radius: 8px;
}

/* ── Buttons ── */
.stButton button {
    background: var(--accent-gradient) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(108, 99, 255, 0.35) !important;
}

/* ── Back Button ── */
.back-btn button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
}
.back-btn button:hover {
    border-color: var(--accent) !important;
    color: var(--text-primary) !important;
}

/* ── Tags in sidebar ── */
.sidebar-section-title {
    color: var(--accent);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin-bottom: 0.5rem;
    margin-top: 1.2rem;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
}
.empty-state-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state-text { font-size: 1rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

/* ── Image styling ── */
[data-testid="stImage"] img {
    border-radius: 12px !important;
}

/* ── Horizontal divider ── */
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────

if "view" not in st.session_state:
    st.session_state.view = "list"          # 'list' | 'detail'
if "selected_anime_id" not in st.session_state:
    st.session_state.selected_anime_id = None
if "locale" not in st.session_state:
    st.session_state.locale = "tr"
if "search" not in st.session_state:
    st.session_state.search = ""
if "genre_filter" not in st.session_state:
    st.session_state.genre_filter = "All"
if "min_rating" not in st.session_state:
    st.session_state.min_rating = 0.0
if "max_rating" not in st.session_state:
    st.session_state.max_rating = 10.0

locale = st.session_state.locale


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    # Logo & title
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:2.5rem;">🎌</div>
        <div style="font-size:1.1rem;font-weight:800;background:linear-gradient(135deg,#6c63ff,#e040fb);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            AnimeAI
        </div>
        <div style="font-size:0.7rem;color:#606070;letter-spacing:1px;margin-top:2px;">
            AI-POWERED DISCOVERY
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Language Switcher ──
    st.markdown('<div class="sidebar-section-title">🌐 Dil / Language</div>', unsafe_allow_html=True)
    col_tr, col_en = st.columns(2)
    with col_tr:
        if st.button("🇹🇷 Türkçe", use_container_width=True,
                     type="primary" if locale == "tr" else "secondary"):
            st.session_state.locale = "tr"
            st.rerun()
    with col_en:
        if st.button("🇬🇧 English", use_container_width=True,
                     type="primary" if locale == "en" else "secondary"):
            st.session_state.locale = "en"
            st.rerun()

    # ── Search ──
    st.markdown(
        f'<div class="sidebar-section-title">🔍 {"Ara" if locale == "tr" else "Search"}</div>',
        unsafe_allow_html=True,
    )
    search_placeholder = "Anime adı yazın..." if locale == "tr" else "Search anime title..."
    search_input = st.text_input(
        label="search",
        label_visibility="collapsed",
        placeholder=search_placeholder,
        value=st.session_state.search,
        key="search_input",
    )
    if search_input != st.session_state.search:
        st.session_state.search = search_input
        st.session_state.view = "list"

    # ── Genre Filter ──
    genre_label = "Tür Filtresi" if locale == "tr" else "Genre Filter"
    st.markdown(f'<div class="sidebar-section-title">🎭 {genre_label}</div>', unsafe_allow_html=True)
    genre_labels = {
        "All": "Tümü" if locale == "tr" else "All",
    }
    display_genres = ["All"] + [g for g in GENRES if g != "All"]
    selected_genre = st.selectbox(
        label="genre",
        label_visibility="collapsed",
        options=display_genres,
        index=display_genres.index(st.session_state.genre_filter) if st.session_state.genre_filter in display_genres else 0,
    )
    if selected_genre != st.session_state.genre_filter:
        st.session_state.genre_filter = selected_genre
        st.session_state.view = "list"

    # ── Rating Filter ──
    rating_label = "Puan Aralığı" if locale == "tr" else "Rating Range"
    st.markdown(f'<div class="sidebar-section-title">⭐ {rating_label}</div>', unsafe_allow_html=True)
    rating_range = st.slider(
        label="rating",
        label_visibility="collapsed",
        min_value=0.0,
        max_value=10.0,
        value=(st.session_state.min_rating, st.session_state.max_rating),
        step=0.5,
    )
    if rating_range[0] != st.session_state.min_rating or rating_range[1] != st.session_state.max_rating:
        st.session_state.min_rating, st.session_state.max_rating = rating_range
        st.session_state.view = "list"

    st.markdown("---")
    # Stats footer
    st.markdown(
        f"""
        <div style="color:#606070;font-size:0.72rem;text-align:center;line-height:1.8;">
            <div>📡 Strapi CMS · SQLite</div>
            <div>🤖 OpenAI · Pollinations AI</div>
            <div>🌐 Jikan API (MyAnimeList)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# App Header Banner
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.view == "list":
    title_tr = "🎌 Anime Keşif Platformu"
    title_en = "🎌 Anime Discovery Platform"
    sub_tr = "AI destekli öneri sistemi · Çok dilli içerik · 10,000+ anime"
    sub_en = "AI-powered recommendation system · Multilingual content · 10,000+ anime"
    st.markdown(
        f"""
        <div class="app-header">
            <h1 class="app-title">{"AnimeAI" if locale == "tr" else "AnimeAI"}</h1>
            <p class="app-subtitle">{sub_tr if locale == "tr" else sub_en}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# LIST VIEW
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.view == "list":
    with loading_spinner(locale):
        result = fetch_anime_list(
            locale=locale,
            genre=st.session_state.genre_filter if st.session_state.genre_filter != "All" else None,
            min_rating=st.session_state.min_rating,
            max_rating=st.session_state.max_rating,
            search=st.session_state.search or None,
        )

    # Connection error
    if "error" in result:
        connection_error_banner(locale)
        st.stop()

    anime_list = result.get("data", [])
    meta = result.get("meta", {}).get("pagination", {})
    total = meta.get("total", 0)

    # Results count
    count_text = f"{total} anime bulundu" if locale == "tr" else f"{total} anime found"
    if st.session_state.search:
        count_text += f" · \"{st.session_state.search}\""
    st.markdown(
        f'<p style="color:#9090a0;font-size:0.85rem;margin-bottom:1rem;">{count_text}</p>',
        unsafe_allow_html=True,
    )

    # Empty state — Strapi bagli ama veri yok
    if not anime_list and not st.session_state.search and st.session_state.genre_filter == "All":
        diag = check_strapi_connection()
        if diag.get("ok") and diag.get("count", 0) == 0:
            st.markdown(
                f"""
                <div class="empty-state">
                    <div class="empty-state-icon">🤖</div>
                    <div style="color:#f0f0f5;font-size:1.1rem;font-weight:700;margin-bottom:0.5rem;">
                        {'Henuz veri yok!' if locale == 'tr' else 'No data yet!'}
                    </div>
                    <div class="empty-state-text" style="margin-bottom:1rem;">
                        {'Strapi bagli fakat icinde hic anime yok.' if locale == 'tr'
                         else 'Strapi is connected but has no anime data.'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.info(
                "Python scriptini calistirin:\n"
                "```\n"
                "cd python\n"
                ".\\\\venv\\\\Scripts\\\\Activate.ps1\n"
                "python main.py --skip-images --limit 10\n"
                "```"
            )
            st.stop()

    # Filtre sonucu bos
    if not anime_list:
        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">
                    {"Anime bulunamadı. Filtreleri değiştirmeyi deneyin." if locale == "tr" 
                     else "No anime found. Try changing your filters."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    # Anime Grid (4 columns)
    cols_per_row = 4
    for row_start in range(0, len(anime_list), cols_per_row):
        row_items = anime_list[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, anime_entry in zip(cols, row_items):
            with col:
                clicked = anime_card(
                    anime_entry,
                    locale=locale,
                    key_prefix=f"row{row_start}",
                )
                if clicked:
                    entry_id = anime_entry.get("id") or anime_entry.get("documentId")
                    st.session_state.selected_anime_id = str(entry_id)
                    st.session_state.view = "detail"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# DETAIL VIEW
# ─────────────────────────────────────────────────────────────────────────────

elif st.session_state.view == "detail":
    anime_id = st.session_state.selected_anime_id

    # Back button
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button(lbl("back", locale), key="back_btn"):
        st.session_state.view = "list"
        st.session_state.selected_anime_id = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Fetch detail
    with loading_spinner(locale):
        detail_result = fetch_anime_detail(anime_id, locale=locale)

    if "error" in detail_result:
        connection_error_banner(locale)
        st.stop()

    anime = detail_result.get("data", {})
    if not anime:
        st.error("Anime bulunamadı." if locale == "tr" else "Anime not found.")
        st.stop()

    title = anime.get("title", "Unknown")
    original_title = anime.get("originalTitle", "")
    synopsis = anime.get("synopsis", "") or lbl("no_synopsis", locale)
    genre = anime.get("genre", "")
    studio = anime.get("studio", "")
    year = anime.get("releaseYear", "")
    rating = anime.get("rating")
    cover_image = anime.get("coverImage")
    image_url = get_image_url(cover_image, prefer="large") if cover_image else None

    # ── Detail Header ──
    st.markdown('<div class="detail-header">', unsafe_allow_html=True)
    col_img, col_info = st.columns([1, 2])

    with col_img:
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.markdown(
                '<div class="no-image-placeholder" style="height:360px;border-radius:12px;">🎌</div>',
                unsafe_allow_html=True,
            )

    with col_info:
        st.markdown(f'<h1 class="detail-title">{title}</h1>', unsafe_allow_html=True)
        if original_title and original_title != title:
            st.markdown(
                f'<div class="detail-original-title">Original: {original_title}</div>',
                unsafe_allow_html=True,
            )

        # Genre badge
        st.markdown(f'<div style="margin-bottom:1rem;">{genre_badge(genre)}</div>', unsafe_allow_html=True)

        # Stats row
        st.markdown(
            f"""
            <div class="detail-stats-row">
                <div class="stat-item">
                    <span class="stat-label">⭐ {lbl("rating", locale)}</span>
                    <span class="stat-value">{f"{rating:.1f} / 10" if rating else "N/A"}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">🏢 {lbl("studio", locale)}</span>
                    <span class="stat-value">{studio or "N/A"}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">📅 {lbl("year", locale)}</span>
                    <span class="stat-value">{year or "N/A"}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Synopsis
        st.markdown(
            f'<div class="section-header">📖 {lbl("synopsis", locale)}</div>',
            unsafe_allow_html=True,
        )
        synopsis_clean = synopsis.replace("\n", "<br>") if synopsis else lbl("no_synopsis", locale)
        st.markdown(f'<div class="synopsis-box">{synopsis_clean}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Recommendations Section ──
    st.markdown(
        f'<div class="section-header">🎯 {lbl("recommendations", locale)}</div>',
        unsafe_allow_html=True,
    )

    with loading_spinner(locale):
        recommendations = fetch_recommendations(anime_id, locale=locale)

    if not recommendations:
        st.markdown(
            f"""
            <div class="empty-state" style="padding:2rem;">
                <div class="empty-state-icon">🤖</div>
                <div class="empty-state-text">{lbl("no_recs", locale)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Two-column layout for recommendations
        rec_cols = st.columns(2)
        for idx, rec in enumerate(recommendations):
            with rec_cols[idx % 2]:
                clicked_rec_id = recommendation_card(
                    rec,
                    locale=locale,
                    key_prefix=f"rec_{anime_id}_{idx}",
                )
                if clicked_rec_id:
                    st.session_state.selected_anime_id = clicked_rec_id
                    st.rerun()
