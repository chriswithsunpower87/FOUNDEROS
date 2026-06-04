# FounderOS — How to Run Locally

Complete step-by-step guide. Every command is copy-paste ready.

---

## STEP 1 — Install PostgreSQL (if you don't have it)

Open **Terminal** on your Mac and run these one by one:

```bash
# Install Homebrew (skip if already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL and set it to auto-start on login
brew services start postgresql@15

# Add psql to your PATH (paste into terminal, then press Enter)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify it's running
pg_isready
# Should print: /tmp/.s.PGSQL.5432 - accepting connections
```

---

## STEP 2 — Create the Database

```bash
# Create the founderos database
createdb founderos

# Verify it was created
psql founderos -c "\l" | grep founderos
```

---

## STEP 3 — Install new backend dependencies

New packages were added (slowapi for rate limiting, aiosqlite + pytest for testing):

```bash
cd ~/projects/FOUNDEROS/backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## STEP 4 — Run Database Migrations

```bash
cd ~/projects/FOUNDEROS/backend
source venv/bin/activate

# Runs all pending migrations (001 → 002 → 003)
alembic upgrade head
```

You should see:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add REVENUE_COST agent
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add is_public to ideas
```

---

## STEP 4b — Run the test suite (optional but impressive)

```bash
cd ~/projects/FOUNDEROS/backend
source venv/bin/activate
pytest tests/ -v
```

All tests use an in-memory SQLite DB — no Postgres needed to run tests.

---

## STEP 4 — Reset ChromaDB (RAG knowledge base)

The knowledge files were expanded with richer content. Delete the old vector data so it re-seeds:

```bash
# From the backend folder
rm -rf chroma_db/
```

The backend will automatically re-seed ChromaDB on next startup.

---

## STEP 5 — Start the Backend

```bash
# Make sure you're in backend/ with venv active
cd ~/projects/FOUNDEROS/backend
source venv/bin/activate

# Start FastAPI with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting FounderOS API [development]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open your browser and go to **http://localhost:8000/docs** — you should see the Swagger API docs.

---

## STEP 6 — Start the Frontend

Open a **second Terminal tab** (Cmd+T):

```bash
cd ~/projects/FOUNDEROS/frontend

# Start Next.js dev server
npm run dev
```

You should see:
```
▲ Next.js 15.x.x
- Local:        http://localhost:3000
- Ready in Xs
```

Open your browser and go to **http://localhost:3000**

---

## STEP 7 — Test the Full Flow

1. Go to http://localhost:3000
2. Click **"Get Started Free"** → Register with your email
3. You'll be redirected to the Dashboard
4. Click **"New Idea"** → Fill in your startup idea details
5. Click into the idea → Click **"Analyze"** button
6. Watch all 10 agents run in real-time (progress bar updates)
7. When complete → Download PDF or Markdown blueprint

---

## TROUBLESHOOTING

### "Connection refused" on backend startup
PostgreSQL is not running. Run: `brew services start postgresql@15`

### "Database founderos does not exist"
Run: `createdb founderos` then `alembic upgrade head`

### "429 Quota Exhausted" for Gemini
Your Gemini free-tier daily quota is exhausted. The system automatically falls back to **OpenRouter (free)**. Wait until midnight Pacific for Gemini quota to reset, or add billing at https://aistudio.google.com

### "Module not found" error in backend
Run: `pip install -r requirements.txt` inside the venv

### Frontend shows blank page
Check the browser console (F12). Most likely: backend is not running on port 8000. Start the backend first.

### "Unauthorized" on export
Make sure you're logged in. Refresh the page and try again.

---

## YOUR API KEYS (already in .env)

| Key | Status |
|-----|--------|
| Gemini API Key | ✅ Set |
| OpenRouter API Key | ✅ Set |
| JWT Secret | ✅ Set |
| Database URL | Local PostgreSQL (localhost/founderos) |

---

## ENVIRONMENT FILES

| File | Status |
|------|--------|
| `backend/.env` | ✅ Ready |
| `frontend/.env.local` | ✅ Ready |

---

## HOW THE AI WORKS (when Gemini is quota-limited)

The system automatically falls back to **OpenRouter** (using Llama 3.1 8B Instruct — free). 
This means even with Gemini quota exhausted, the pipeline still runs.
To get better outputs, wait for Gemini quota reset or add a Gemini billing account.
