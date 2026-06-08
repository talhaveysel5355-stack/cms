# Project Report
## AI-Powered Multilingual Anime Recommendation and Discovery System

**Course:** Content Management Systems / Web Technologies  
**Project Type:** Full-Stack Software Development  
**Technology Stack:** Strapi · Python · Streamlit · OpenAI · SQLite  
**Date:** June 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [System Architecture](#3-system-architecture)
4. [Technology Choices & Justification](#4-technology-choices--justification)
5. [Implementation Details](#5-implementation-details)
6. [Database Design](#6-database-design)
7. [API Design](#7-api-design)
8. [AI Integration](#8-ai-integration)
9. [Multilingual Support](#9-multilingual-support)
10. [Results & Demonstration](#10-results--demonstration)
11. [Challenges & Solutions](#11-challenges--solutions)
12. [Conclusion & Future Work](#12-conclusion--future-work)
13. [References](#13-references)

---

## 1. Introduction

This project implements a full-stack **AI-Powered Multilingual Anime Recommendation and Discovery System**. The system integrates a content management system (Strapi CMS), an automated Python data pipeline, and a Streamlit user interface to provide personalized anime recommendations enriched with artificial intelligence.

The core idea is to demonstrate how modern CMS platforms can be combined with AI APIs to create intelligent, multilingual content experiences. The system automatically collects anime data from public databases, enhances it with AI-generated content in two languages (Turkish and English), and presents it through a visually rich, interactive web interface.

---

## 2. Problem Statement & Motivation

### Problem
Anime enthusiasts face two major challenges:
1. **Discovery Problem**: With over 20,000 anime titles in existence, finding new shows that match one's taste is difficult and time-consuming.
2. **Language Barrier**: Most anime databases (e.g., MyAnimeList) primarily provide English content, leaving non-English speakers with limited localized information.

### Motivation
This project addresses both problems by:
- **Automating content collection** from public anime APIs
- **Generating AI-powered recommendations** explaining *why* a specific anime is recommended
- **Providing Turkish-language content** through automatic translation and AI generation
- **Creating a unified CMS** that stores both the original and enriched content in a structured, queryable format

### Learning Objectives
- Understand headless CMS architecture with Strapi
- Apply REST API integration patterns
- Integrate Large Language Models (LLMs) into real-world workflows
- Build end-to-end data pipelines
- Design responsive web UIs with Python

---

## 3. System Architecture

The system follows a **three-tier architecture** with an automated ETL (Extract, Transform, Load) pipeline:

```
[External APIs] → [Python ETL Engine] → [Strapi CMS] ← [Streamlit Frontend] ← [User]
```

### Tier 1: Data Collection & AI Enrichment (Python)
The Python automation engine acts as the "brain" of the system. It fetches raw anime data, enriches it with AI, and stores it in the CMS.

### Tier 2: Content Management System (Strapi)
Strapi serves as the central data store and REST API provider. It manages content in two languages (TR/EN), handles media uploads, and enforces data validation.

### Tier 3: User Interface (Streamlit)
The Streamlit frontend queries Strapi's REST API and presents anime in a visually engaging, filterable interface with language switching.

For the complete architecture diagram, see [architecture_diagram.md](./architecture_diagram.md).

---

## 4. Technology Choices & Justification

### 4.1 Strapi (Headless CMS)

**Chosen because:**
- Open-source with a vibrant community
- Built-in REST API generation (no manual route writing)
- Content-type builder with visual schema editor
- Native internationalization (i18n) support in v5
- Media library with automatic image resizing
- Role-based access control

**Alternative considered:** WordPress + WooCommerce REST API — rejected because it is not built for API-first usage and has a more complex PHP codebase.

### 4.2 Python Automation Engine

**Chosen because:**
- Excellent library ecosystem for HTTP, AI, and data processing
- `openai` official SDK provides clean LLM integration
- `deep-translator` offers free translation without API keys
- `requests` library makes REST API integration trivial
- Cross-platform and widely taught in academic settings

### 4.3 Streamlit

**Chosen because:**
- Builds data-centric UIs purely in Python (no JavaScript required)
- Rapid prototyping with session state management
- Easy deployment and sharing
- Natively integrates with Python data science libraries

**Alternative considered:** React.js — rejected because it requires JavaScript/TypeScript expertise beyond the scope of this project.

### 4.4 OpenAI GPT-4o-mini

**Chosen because:**
- Most cost-effective model with strong language understanding
- Supports both Turkish and English generation
- Available via simple REST API
- Well-documented with an official Python SDK

### 4.5 Pollinations AI

**Chosen because:**
- **Completely free** — no API key or registration required
- Simple REST endpoint (`/prompt/{description}`)
- Generates high-quality anime-style artwork
- No rate limits for reasonable usage

### 4.6 Jikan API

**Chosen because:**
- Unofficial MyAnimeList REST API — free and public
- Returns structured anime data (title, synopsis, genres, ratings, images)
- No authentication required
- Rate-limited to 3 requests/second (handled with sleep delays)

---

## 5. Implementation Details

### 5.1 Python Automation Engine

The engine is structured as a pipeline of independent modules:

```
main.py (Orchestrator)
├── jikan_client.py    → HTTP client for Jikan API
├── ai_enricher.py     → OpenAI + Google Translate
├── image_generator.py → Pollinations AI poster generation
└── strapi_client.py   → Strapi REST API integration
```

**Pipeline flow for each anime:**
1. Fetch from Jikan (English data)
2. Translate synopsis: English → Turkish
3. Expand synopsis with OpenAI (both TR and EN versions)
4. Generate AI poster via Pollinations (768×1024px)
5. Download original cover from MyAnimeList CDN
6. Upload both images to Strapi Media Library
7. Create Anime entry in Strapi (Turkish locale)
8. Add English locale to same document
9. Publish the entry

**Recommendation Generation:**
For each pair of anime with shared genres, the system:
1. Computes a **Jaccard similarity score**: `|genres_A ∩ genres_B| / |genres_A ∪ genres_B|`
2. Selects the top-3 most similar anime for each source
3. Calls OpenAI to generate a natural-language recommendation reason in both TR and EN
4. Stores the recommendation with source anime, target anime, reason, and score

### 5.2 Strapi Content Architecture

Two content-types were designed:

**Anime Collection:**
- 10 fields total (title, originalTitle, synopsis, genre, studio, releaseYear, rating, coverImage, malId, recommendations)
- `title` and `synopsis` are localized (different values per language)
- All other fields are shared across locales
- Draft/publish workflow enabled

**Recommendation Collection:**
- `recommendationReason` is localized
- `similarityScore` is a decimal (0–1)
- Two relations: `anime` (source) and `recommendedAnime` (target)

### 5.3 Streamlit Frontend

The UI uses **session state** for client-side navigation without page reloads:
- `st.session_state.view` controls active view (`"list"` or `"detail"`)
- `st.session_state.selected_anime_id` stores the clicked anime's Strapi ID
- `st.session_state.locale` stores the selected language

The dark anime theme is implemented via a 200-line custom CSS block injected with `st.markdown(unsafe_allow_html=True)`. Key design decisions:
- **Glassmorphism cards** with CSS `backdrop-filter`
- **Purple-to-magenta gradient** inspired by premium anime platforms
- **Progress bars** for similarity scores
- **Google Fonts (Outfit)** for modern typography

---

## 6. Database Design

The system uses **SQLite** as the database, managed through Strapi's Knex.js ORM. The key tables are:

- `animes` — Stores all anime metadata + locale versions
- `recommendations` — Stores AI-generated recommendations with FK relations
- `files` — Strapi media library (cover images + AI posters)
- `strapi_users_permissions_users` — API authentication users

For the complete schema with field types and constraints, see [database_schema.md](./database_schema.md).

**Key design decisions:**
- `mal_id` field has a UNIQUE constraint to prevent duplicate imports
- The `document_id` field (Strapi 5) links TR and EN versions of the same record
- Relations use Strapi's built-in FK management (no manual JOIN queries needed)

---

## 7. API Design

The project exposes a REST API through Strapi with the following key endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/auth/local` | JWT authentication |
| `GET` | `/api/animes` | List anime with filters |
| `GET` | `/api/animes/:id` | Anime detail + recommendations |
| `POST` | `/api/animes` | Create anime entry |
| `PUT` | `/api/animes/:id` | Update/add locale |
| `GET` | `/api/recommendations` | List recommendations |
| `POST` | `/api/recommendations` | Create recommendation |
| `POST` | `/api/upload` | Upload media file |

The API uses **Strapi's built-in filtering system** with operators like `$eq`, `$gte`, `$containsi` for powerful querying without custom route logic.

For complete request/response examples, see [api_documentation.md](./api_documentation.md).

---

## 8. AI Integration

### 8.1 Synopsis Expansion (OpenAI)

**Prompt engineering approach:**
The system uses a structured prompt that instructs GPT-4o-mini to write a 3-paragraph synopsis covering: (1) story premise, (2) character motivations, (3) unique selling points. This ensures consistent output structure across all anime.

```python
prompt = f"""You are an anime expert writer. Write a detailed, engaging 3-paragraph 
summary in Turkish that covers:
1. The main story premise and setting
2. The key characters and their motivations  
3. What makes this anime unique and worth watching
...
```

**Temperature setting:** 0.7 — balances creativity with coherence.

### 8.2 Recommendation Reasons (OpenAI)

The system generates concise recommendation explanations (max 40 words) that always start with "Önerilir çünkü..." (TR) or "Recommended because..." (EN). The prompt provides genre overlap information to guide the AI toward relevant explanations.

### 8.3 AI Image Generation (Pollinations AI)

Images are generated using a structured prompt template:
```
"cinematic anime poster for '{title}', {genre_str} style, vibrant colors, 
high detail, dramatic lighting, professional anime artwork, Studio Ghibli quality,
epic composition, atmospheric, 4K resolution"
```

The `seed` parameter is derived from the anime title hash to ensure reproducible results.

### 8.4 Translation (deep-translator)

The `GoogleTranslator` class from `deep-translator` handles EN→TR translation:
- No API key required (uses Google Translate's public endpoint)
- Handles up to ~5000 characters per request
- Falls back to original text on translation failure

---

## 9. Multilingual Support

Strapi 5 includes native internationalization (i18n) built into the core:

**Configuration:**
- Default locale: **Turkish (tr)**
- Additional locale: **English (en)**
- Localized fields: `title`, `synopsis` (Anime), `recommendationReason` (Recommendation)
- Shared fields: `genre`, `studio`, `rating`, `malId`, `coverImage`

**API usage:**
```
GET /api/animes?locale=tr  → Returns Turkish content
GET /api/animes?locale=en  → Returns English content
```

**Streamlit implementation:**
The language switcher in the sidebar updates `st.session_state.locale` and triggers a `st.rerun()`, causing all API calls to use the new locale parameter. This provides instant language switching without page navigation.

---

## 10. Results & Demonstration

### System Capabilities Achieved

| Feature | Status |
|---------|--------|
| Anime data collection from Jikan API | ✅ Complete |
| AI synopsis expansion (Turkish) | ✅ Complete |
| AI synopsis expansion (English) | ✅ Complete |
| EN→TR translation | ✅ Complete |
| AI poster generation (Pollinations) | ✅ Complete |
| Strapi JWT authentication | ✅ Complete |
| Image upload to Media Library | ✅ Complete |
| Anime CRUD with i18n | ✅ Complete |
| Recommendation generation (AI) | ✅ Complete |
| Recommendation CRUD | ✅ Complete |
| Streamlit dark-themed UI | ✅ Complete |
| Genre filtering | ✅ Complete |
| Rating range filtering | ✅ Complete |
| Full-text search | ✅ Complete |
| Detail page with AI poster | ✅ Complete |
| Language switcher (TR/EN) | ✅ Complete |
| Recommendation cards with AI reasons | ✅ Complete |
| Similarity score progress bars | ✅ Complete |

### Performance Metrics

| Operation | Approximate Time |
|-----------|-----------------|
| Fetch 20 anime from Jikan | ~15 seconds |
| Translate 20 synopses | ~30 seconds |
| Expand 20 synopses with AI | ~60 seconds |
| Generate 20 AI posters | ~90 seconds |
| Upload images to Strapi | ~40 seconds |
| Generate 60 recommendations | ~45 seconds |
| **Total pipeline (20 anime)** | **~5-6 minutes** |

---

## 11. Challenges & Solutions

### Challenge 1: Strapi 5 i18n Plugin Change
**Problem:** Strapi 5 made i18n a core feature, removing the need for `@strapi/plugin-i18n`. Attempting to install it causes dependency conflicts.  
**Solution:** Removed the plugin import and configured locales directly through the Strapi Admin panel under Settings → Internationalization.

### Challenge 2: Jikan API Rate Limiting
**Problem:** Jikan API allows only 3 requests/second; exceeding this returns HTTP 429 errors.  
**Solution:** Added `time.sleep(0.5)` between all API calls in `jikan_client.py`.

### Challenge 3: Pollinations AI Response Variability
**Problem:** The Pollinations AI endpoint occasionally returns HTML error pages instead of image bytes.  
**Solution:** Added content-type validation — if the response is not `image/*` or is smaller than 1KB, it is discarded and logged.

### Challenge 4: Strapi 5 Document ID vs. Numeric ID
**Problem:** Strapi 5 uses both numeric `id` and string `documentId` fields. Some API calls require one, some require the other.  
**Solution:** The `strapi_client.py` handles both by checking `entry.get('id') or entry.get('documentId')` and the Streamlit `api_client.py` passes whichever is available.

### Challenge 5: Large Streamlit Session State
**Problem:** Storing entire anime objects in session state caused re-rendering issues.  
**Solution:** Only the minimal `selected_anime_id` is stored in session state; the full detail is fetched fresh on the detail page.

---

## 12. Conclusion & Future Work

### Conclusion

This project successfully demonstrates a complete end-to-end AI-powered content management system. The integration of Strapi CMS, OpenAI, Pollinations AI, Jikan API, and Streamlit creates a production-quality multilingual anime discovery platform. The system architecture is modular and extensible — each component can be improved or replaced independently.

Key achievements:
1. **Full pipeline automation**: From raw API data to AI-enriched CMS content in one command
2. **Genuine AI value**: Recommendation explanations go beyond genre tags to provide human-readable insight
3. **Multilingual content**: Turkish-first approach with seamless English switching
4. **Professional UI**: Dark anime-streaming-platform aesthetic with glassmorphism design

### Future Work

| Enhancement | Priority | Effort |
|-------------|----------|--------|
| User authentication (favorites, watch list) | High | Medium |
| Collaborative filtering (user-based recommendations) | High | High |
| PostgreSQL migration for production | Medium | Low |
| Streaming video trailer integration | Medium | High |
| Mobile-responsive Streamlit layout | Low | Medium |
| Webhook-based real-time updates | Low | High |
| Anime episode tracking | Low | High |
| Discord bot integration | Low | Medium |

---

## 13. References

1. **Strapi Documentation** — https://docs.strapi.io  
   *Official Strapi v5 documentation covering content-type builder, REST API, and i18n.*

2. **Jikan API Documentation** — https://docs.api.jikan.moe  
   *Unofficial MyAnimeList REST API reference. Rate limits and endpoint specifications.*

3. **OpenAI API Reference** — https://platform.openai.com/docs/api-reference  
   *Official documentation for GPT-4o-mini and chat completions endpoint.*

4. **Pollinations AI** — https://pollinations.ai  
   *Free AI image generation service documentation and prompt guide.*

5. **deep-translator** — https://github.com/nidhaloff/deep-translator  
   *Python library for translation using multiple providers including Google Translate.*

6. **Streamlit Documentation** — https://docs.streamlit.io  
   *Official Streamlit reference for session state, layout, and custom components.*

7. **MyAnimeList** — https://myanimelist.net  
   *Source database for anime ratings, genres, and metadata accessed via Jikan API.*

8. **Knex.js Documentation** — https://knexjs.org  
   *SQL query builder used internally by Strapi for SQLite and PostgreSQL.*

9. **SQLite Documentation** — https://www.sqlite.org/docs.html  
   *Embedded database engine documentation.*

10. **Jaccard Similarity** — Jaccard, P. (1912). *The distribution of the flora in the alpine zone.* New Phytologist, 11(2), 37–50.  
    *Mathematical basis for the genre-based similarity scoring algorithm used in recommendation generation.*
