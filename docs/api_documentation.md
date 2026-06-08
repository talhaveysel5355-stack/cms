# API Documentation — AI-Powered Multilingual Anime Recommendation System

## Base URL
```
http://localhost:1337/api
```

All endpoints return JSON. Authenticated endpoints require a Bearer JWT token.

---

## Authentication

### POST `/api/auth/local`
Authenticate a registered user and receive a JWT token.

**Request:**
```json
POST /api/auth/local
Content-Type: application/json

{
  "identifier": "admin@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

**Usage in subsequent requests:**
```http
Authorization: Bearer <jwt>
```

---

## Anime Endpoints

### GET `/api/animes`
Fetch a paginated list of anime entries.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `locale` | string | `tr` (default) or `en` |
| `pagination[page]` | integer | Page number (default: 1) |
| `pagination[pageSize]` | integer | Items per page (default: 25, max: 100) |
| `filters[genre][$eq]` | string | Filter by genre (e.g. `Action`) |
| `filters[rating][$gte]` | number | Minimum rating |
| `filters[rating][$lte]` | number | Maximum rating |
| `filters[title][$containsi]` | string | Case-insensitive title search |
| `sort` | string | e.g. `rating:desc`, `title:asc` |
| `populate[coverImage]` | string | Include cover image data |
| `publicationState` | string | `live` (published only) or `preview` |

**Example Request:**
```
GET /api/animes?locale=tr&filters[genre][$eq]=Action&filters[rating][$gte]=8&sort=rating:desc&populate[coverImage][fields][0]=url&pagination[pageSize]=10&publicationState=live
```

**Example Response:**
```json
{
  "data": [
    {
      "id": 1,
      "documentId": "abc123",
      "title": "Fullmetal Alchemist: Brotherhood",
      "originalTitle": "Hagane no Renkinjutsushi: Fullmetal Alchemist",
      "synopsis": "...",
      "genre": "Action",
      "studio": "Bones",
      "releaseYear": 2009,
      "rating": 9.1,
      "malId": 5114,
      "locale": "tr",
      "coverImage": {
        "id": 42,
        "url": "/uploads/fmab_cover_abc123.jpg",
        "formats": {
          "thumbnail": { "url": "/uploads/thumbnail_fmab_cover.jpg" },
          "small": { "url": "/uploads/small_fmab_cover.jpg" },
          "medium": { "url": "/uploads/medium_fmab_cover.jpg" }
        }
      },
      "createdAt": "2024-06-01T12:00:00.000Z",
      "updatedAt": "2024-06-01T12:00:00.000Z",
      "publishedAt": "2024-06-01T12:00:00.000Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "pageCount": 3,
      "total": 25
    }
  }
}
```

---

### GET `/api/animes/:id`
Fetch a single anime with full details and related recommendations.

**Example Request:**
```
GET /api/animes/1?locale=tr&populate[coverImage][fields][0]=url&populate[recommendations][populate][recommendedAnime][populate][coverImage][fields][0]=url&publicationState=live
```

**Example Response:**
```json
{
  "data": {
    "id": 1,
    "documentId": "abc123",
    "title": "Fullmetal Alchemist: Brotherhood",
    "synopsis": "Psikolojik temaları ve güçlü karakter gelişimiyle öne çıkan...",
    "genre": "Action",
    "studio": "Bones",
    "releaseYear": 2009,
    "rating": 9.1,
    "malId": 5114,
    "coverImage": {
      "url": "/uploads/fmab_cover.jpg"
    },
    "recommendations": [
      {
        "id": 1,
        "recommendationReason": "Önerilir çünkü FMA gibi derin karakter gelişimi ve duygusal ağırlık taşımaktadır.",
        "similarityScore": 0.85,
        "recommendedAnime": {
          "id": 2,
          "title": "Attack on Titan",
          "genre": "Action",
          "rating": 9.0,
          "coverImage": { "url": "/uploads/aot_cover.jpg" }
        }
      }
    ]
  }
}
```

---

### POST `/api/animes`
Create a new anime entry. Requires JWT authentication.

**Request:**
```json
POST /api/animes
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "data": {
    "title": "Naruto",
    "originalTitle": "NARUTO -ナルト-",
    "synopsis": "Naruto Uzumaki, güçlü olmak isteyen genç bir ninja...",
    "genre": "Action",
    "studio": "Pierrot",
    "releaseYear": 2002,
    "rating": 7.9,
    "malId": 20,
    "locale": "tr"
  }
}
```

**Response:**
```json
{
  "data": {
    "id": 5,
    "documentId": "xyz789",
    "title": "Naruto",
    ...
  }
}
```

---

### PUT `/api/animes/:id`
Update an existing anime entry (e.g., add EN locale). Requires JWT.

**Add English locale:**
```json
PUT /api/animes/5
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "data": {
    "title": "Naruto",
    "synopsis": "Naruto Uzumaki is a young ninja who desires to become...",
    "locale": "en"
  }
}
```

---

## Recommendation Endpoints

### GET `/api/recommendations`
Fetch recommendations, optionally filtered by source anime.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `locale` | string | `tr` or `en` |
| `filters[anime][id][$eq]` | integer | Filter by source anime ID |
| `populate[recommendedAnime]` | — | Include recommended anime data |
| `sort` | string | e.g. `similarityScore:desc` |
| `pagination[pageSize]` | integer | Max results |

**Example Request:**
```
GET /api/recommendations?locale=tr&filters[anime][id][$eq]=1&populate[recommendedAnime][populate][coverImage][fields][0]=url&sort=similarityScore:desc&pagination[pageSize]=6
```

---

### POST `/api/recommendations`
Create a new recommendation. Requires JWT.

**Request:**
```json
POST /api/recommendations
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "data": {
    "recommendationReason": "Önerilir çünkü aynı psikolojik temalar ve güçlü karakter gelişimi paylaşılmaktadır.",
    "similarityScore": 0.78,
    "anime": 1,
    "recommendedAnime": 3,
    "locale": "tr"
  }
}
```

---

## Media Upload Endpoint

### POST `/api/upload`
Upload an image file to the Strapi Media Library. Requires JWT.

**Request (multipart/form-data):**
```
POST /api/upload
Authorization: Bearer <jwt>
Content-Type: multipart/form-data

files: <image binary>
ref: api::anime.anime        (optional: link to content type)
refId: 1                     (optional: link to specific entry ID)
field: coverImage            (optional: field name)
```

**Response:**
```json
[
  {
    "id": 42,
    "name": "naruto_cover.jpg",
    "url": "/uploads/naruto_cover_abc123.jpg",
    "mime": "image/jpeg",
    "size": 245.6,
    "width": 768,
    "height": 1024,
    "formats": {
      "thumbnail": { "url": "/uploads/thumbnail_naruto_cover.jpg", "width": 156, "height": 207 },
      "small": { "url": "/uploads/small_naruto_cover.jpg", "width": 375, "height": 499 },
      "medium": { "url": "/uploads/medium_naruto_cover.jpg", "width": 750, "height": 998 }
    }
  }
]
```

---

## Filtering Reference

Strapi 5 REST API filter operators:

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `$eq` | `=` | `filters[genre][$eq]=Action` |
| `$ne` | `!=` | `filters[genre][$ne]=Comedy` |
| `$lt` | `<` | `filters[rating][$lt]=5` |
| `$lte` | `<=` | `filters[rating][$lte]=7` |
| `$gt` | `>` | `filters[rating][$gt]=8` |
| `$gte` | `>=` | `filters[rating][$gte]=8` |
| `$in` | `IN (...)` | `filters[genre][$in][0]=Action&filters[genre][$in][1]=Drama` |
| `$contains` | `LIKE %val%` | `filters[title][$contains]=naruto` |
| `$containsi` | `ILIKE %val%` | `filters[title][$containsi]=NARUTO` |

---

## Error Responses

All errors follow this format:
```json
{
  "data": null,
  "error": {
    "status": 400,
    "name": "ValidationError",
    "message": "...",
    "details": {}
  }
}
```

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Validation error |
| `401` | Unauthorized (missing/invalid JWT) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not found |
| `500` | Internal server error |
