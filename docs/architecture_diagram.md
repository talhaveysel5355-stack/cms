# System Architecture — AI-Powered Multilingual Anime Recommendation System

## High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Internet["🌐 External APIs"]
        JIKAN["Jikan API\n(MyAnimeList)\napi.jikan.moe/v4"]
        OPENAI["OpenAI API\ngpt-4o-mini"]
        POLLINATIONS["Pollinations AI\nFree Image Generation"]
        GTRANSLATE["Google Translate\n(deep-translator)"]
    end

    subgraph PythonEngine["🐍 Python Automation Engine"]
        MAIN["main.py\nOrchestrator"]
        JIKAN_CLIENT["jikan_client.py\nData Fetcher"]
        AI_ENRICHER["ai_enricher.py\nText AI + Translation"]
        IMG_GEN["image_generator.py\nPoster Generator"]
        STRAPI_CLIENT["strapi_client.py\nCMS Uploader"]
    end

    subgraph StrapiCMS["📦 Strapi CMS (Port 1337)"]
        STRAPI_API["REST API\n/api/animes\n/api/recommendations\n/api/upload"]
        STRAPI_ADMIN["Admin Panel\n/admin"]
        DB[(SQLite Database\n.tmp/data.db)]
        MEDIA[("Media Library\n/public/uploads")]

        subgraph Collections["Content Collections"]
            ANIME_COL["Anime Collection\n(TR + EN locales)"]
            REC_COL["Recommendation Collection\n(TR + EN locales)"]
        end
    end

    subgraph StreamlitApp["🖥️ Streamlit Frontend (Port 8501)"]
        APP["app.py\nMain Application"]
        API_CLIENT["api_client.py\nHTTP Client"]
        COMPONENTS["components.py\nUI Components"]
        subgraph Views["Views"]
            LIST_VIEW["List View\nSearch · Filter · Grid"]
            DETAIL_VIEW["Detail View\nSynopsis · Poster · Recs"]
        end
    end

    subgraph UserBrowser["👤 User Browser"]
        USER["User"]
    end

    %% Data Flow — Python Engine
    JIKAN --> JIKAN_CLIENT
    OPENAI --> AI_ENRICHER
    POLLINATIONS --> IMG_GEN
    GTRANSLATE --> AI_ENRICHER
    JIKAN_CLIENT --> MAIN
    AI_ENRICHER --> MAIN
    IMG_GEN --> MAIN
    MAIN --> STRAPI_CLIENT
    STRAPI_CLIENT --> STRAPI_API

    %% Strapi Internal
    STRAPI_API --> Collections
    STRAPI_API --> MEDIA
    Collections --> DB
    MEDIA --> DB

    %% Streamlit → Strapi
    APP --> API_CLIENT
    API_CLIENT --> STRAPI_API
    APP --> COMPONENTS
    COMPONENTS --> Views

    %% User interaction
    USER --> StreamlitApp
    USER --> STRAPI_ADMIN
    STRAPI_ADMIN --> STRAPI_API
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant SF as Streamlit App
    participant SC as Strapi CMS
    participant PY as Python Engine
    participant JK as Jikan API
    participant AI as OpenAI
    participant PL as Pollinations AI

    Note over PY,PL: Offline ETL Pipeline (run once)
    PY->>JK: GET /top/anime?page=1&limit=25
    JK-->>PY: Anime list (title, synopsis, genres, rating...)
    PY->>AI: Expand synopsis (Turkish + English)
    AI-->>PY: Enriched synopsis text
    PY->>PL: GET /prompt/{anime_poster_prompt}
    PL-->>PY: Image bytes (JPEG)
    PY->>SC: POST /api/upload (cover image)
    SC-->>PY: Media ID
    PY->>SC: POST /api/animes (TR locale)
    SC-->>PY: Document ID
    PY->>SC: PUT /api/animes/{id} (EN locale)
    PY->>AI: Generate recommendation reason (TR + EN)
    AI-->>PY: Recommendation text
    PY->>SC: POST /api/recommendations
    SC-->>PY: Recommendation ID

    Note over U,SC: User Discovery Flow
    U->>SF: Open browser (localhost:8501)
    U->>SF: Search / filter / select language
    SF->>SC: GET /api/animes?locale=tr&filters...
    SC-->>SF: Anime list (with images)
    SF->>U: Render anime grid cards
    U->>SF: Click anime card
    SF->>SC: GET /api/animes/{id}?populate=recommendations
    SC-->>SF: Full detail + recommendations
    SF->>U: Render detail page + AI recommendation cards
```

---

## Component Responsibilities

| Component | Technology | Responsibility |
|-----------|------------|---------------|
| **Strapi CMS** | Node.js / TypeScript | Content storage, REST API, media library, i18n |
| **Python Engine** | Python 3.11+ | Data collection, AI enrichment, image generation, CMS population |
| **Streamlit App** | Python / Streamlit | User-facing discovery UI, search, filters, recommendations |
| **SQLite DB** | SQLite3 | Persistent storage for all CMS data |
| **Jikan API** | REST API | Free MyAnimeList data proxy (rate-limited) |
| **OpenAI** | GPT-4o-mini | Synopsis expansion, recommendation text generation |
| **Pollinations AI** | REST API | Free AI image generation (no API key required) |
| **deep-translator** | Python lib | TR↔EN translation via Google Translate |

---

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────┐
│  Frontend         Streamlit 1.35+  (Python)          │
├─────────────────────────────────────────────────────┤
│  CMS Backend      Strapi 5.x       (Node.js/TS)      │
├─────────────────────────────────────────────────────┤
│  Automation       Python 3.11+                       │
│  ├─ HTTP          requests                           │
│  ├─ AI Text       openai (gpt-4o-mini)               │
│  ├─ Translation   deep-translator (Google)           │
│  └─ AI Images     Pollinations AI (REST)             │
├─────────────────────────────────────────────────────┤
│  Database         SQLite 3 (via Strapi)              │
├─────────────────────────────────────────────────────┤
│  External APIs    Jikan v4 (MyAnimeList)             │
└─────────────────────────────────────────────────────┘
```
