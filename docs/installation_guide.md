# Installation & Setup Guide
## AI-Powered Multilingual Anime Recommendation System

---

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Node.js | 20.x | `node --version` |
| npm | 6.x | `npm --version` |
| Python | 3.11+ | `python --version` |
| pip | 23+ | `pip --version` |

---

## Step 1 — Clone & Open Project

```bash
# The project is already at:
cd "c:\Users\VEYSEL\Desktop\visual code\içerik\icrik_final"
```

---

## Step 2 — Strapi CMS Setup

### 2a. Install Node dependencies
```bash
npm install
```

### 2b. Start Strapi development server
```bash
npm run dev
```

Strapi will start at: **http://localhost:1337**

### 2c. Create admin account (first run only)
1. Open **http://localhost:1337/admin**
2. Fill in the registration form (name, email, password)
3. **Save these credentials** — you'll need them for the Python engine

### 2d. Configure Internationalization
1. Go to **Settings → Internationalization**
2. Click **Add new locale**
3. Select **Turkish (tr)** → set as default
4. Click **Add new locale** again
5. Select **English (en)**

### 2e. Set API Permissions
For the Streamlit frontend to read data without authentication:
1. Go to **Settings → Users & Permissions → Roles → Public**
2. Under **Anime**: enable `find` and `findOne`
3. Under **Recommendation**: enable `find` and `findOne`
4. Under **Upload**: enable `find`
5. Click **Save**

### 2f. Create a regular API user (for Python engine)
1. Go to **Content Manager → User**
2. Click **Create new entry**
3. Set username, email, password
4. Set Role to **Authenticated**
5. Toggle **Confirmed** to ON
6. Click **Save & Publish**

> **Note:** The Python engine authenticates via `/api/auth/local` using a regular user account, not the admin account.

---

## Step 3 — Python Automation Engine Setup

### 3a. Navigate to python folder
```bash
cd python
```

### 3b. Create virtual environment
```bash
python -m venv venv
```

### 3c. Activate virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 3d. Install dependencies
```bash
pip install -r requirements.txt
```

### 3e. Create and configure .env file
```bash
copy .env.example .env
```

Edit `.env` with your values:
```dotenv
# Strapi CMS
STRAPI_URL=http://localhost:1337
STRAPI_ADMIN_EMAIL=your-api-user@email.com
STRAPI_ADMIN_PASSWORD=your-api-user-password

# OpenAI API (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4o-mini

# Number of anime to fetch per run
ANIME_FETCH_LIMIT=20
```

> **No OpenAI key?** The script still works — it will use original synopses and simple template-based recommendation reasons.

### 3f. Run the automation engine

**Full run (recommended first time):**
```bash
python main.py
```

**Test without saving to Strapi:**
```bash
python main.py --dry-run
```

**Faster run (skip AI image generation):**
```bash
python main.py --skip-images --limit 10
```

**All options:**
```
python main.py --help

Options:
  --dry-run       Run without saving to Strapi
  --skip-images   Skip AI poster generation
  --skip-ai       Skip OpenAI enrichment
  --limit N       Process only N anime (default: 20)
```

Expected output:
```
============================================================
  Anime Recommendation Automation Engine
============================================================
[Strapi] ✓ Authenticated as user@email.com
[Main] Found 0 existing anime in Strapi

[Jikan] Fetching top 20 anime...
[Jikan]   ✓ Fullmetal Alchemist: Brotherhood (MAL ID: 5114)
...

[Main] Processing: Fullmetal Alchemist: Brotherhood
────────────────────────────────────────────────────────────
[Translator] Translating synopsis...
[AI] ✓ Expanded synopsis for 'Fullmetal Alchemist...' (542 chars)
[Image] Generating poster for 'Fullmetal Alchemist...'...
[Image] ✓ Generated poster (185432 bytes)
[Strapi] ✓ Uploaded image → ID 1
[Strapi] ✓ Created anime 'Fullmetal Alchemist...' → ID 1
...
============================================================
  Pipeline complete!
  Anime processed: 20
  Strapi URL: http://localhost:1337/admin
============================================================
```

---

## Step 4 — Streamlit Frontend Setup

### 4a. Navigate to streamlit folder
```bash
cd streamlit
```

### 4b. Create virtual environment (separate from Python engine)
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4c. Install dependencies
```bash
pip install -r requirements.txt
```

### 4d. Run the Streamlit app
```bash
streamlit run app.py
```

The app will open automatically at: **http://localhost:8501**

---

## Step 5 — Verify Everything Works

| Check | URL / Command | Expected Result |
|-------|--------------|----------------|
| Strapi admin | http://localhost:1337/admin | Login page |
| Strapi API | http://localhost:1337/api/animes?publicationState=live | JSON with anime list |
| Streamlit | http://localhost:8501 | Dark-themed anime grid |
| Python test | `python main.py --dry-run --limit 3` | No Strapi errors |

---

## Troubleshooting

### "Cannot connect to Strapi"
- Make sure `npm run dev` is running in the `icrik_final` folder
- Check that port 1337 is not blocked by another process: `netstat -ano | findstr 1337`

### "Authentication failed" (Python engine)
- Make sure you created a **regular user** (not admin) in Strapi
- The user must be **confirmed** and have the **Authenticated** role
- Double-check the email/password in `python/.env`

### "No anime found" in Streamlit
- Run `python main.py` first to populate data
- Check that anime entries are **published** in Strapi admin
- Verify Public role has `find` permission on Anime

### PowerShell script execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Jikan API rate limiting
The script includes built-in delays (0.5s between requests). If you see 429 errors, increase the delay in `jikan_client.py`:
```python
time.sleep(1.0)  # Increase to 1 second
```

---

## Running All Components Together

Open **3 separate terminal windows**:

**Terminal 1 — Strapi CMS:**
```bash
cd "c:\Users\VEYSEL\Desktop\visual code\içerik\icrik_final"
npm run dev
```

**Terminal 2 — Python Engine (run once to populate):**
```bash
cd "c:\Users\VEYSEL\Desktop\visual code\içerik\icrik_final\python"
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 3 — Streamlit Frontend:**
```bash
cd "c:\Users\VEYSEL\Desktop\visual code\içerik\icrik_final\streamlit"
.\venv\Scripts\Activate.ps1
streamlit run app.py
```
