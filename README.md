# FanGap

**Comparing what critics say versus what players actually feel — and tracking how that gap changes over time.**

FanGap aggregates video game ratings from Steam, OpenCritic, and IGDB onto a shared 0–100 scale.

**Hybrid model:** search and browse **many games** via IGDB with **live** critic vs player scores. Only the **Featured Top 10** in Postgres keep **monthly snapshot history** and trend charts; the set rotates when live divergence ranking changes.

![Game list with search and filters](docs/screenshots/games.png)

![Score trend on a game detail page](docs/screenshots/detail.png)

![Divergence leaderboard](docs/screenshots/leaderboard.png)

---

## Features

- **IGDB catalog search** — browse many titles; live multi-source scores on each detail page
- **Live divergence leaderboard** — cached ranking (~50) rebuilt from an IGDB candidate pool
- **Featured Top 10** — Postgres snapshots + monthly chart; games dropped from the top 10 lose stored history
- **Multi-source aggregation** — Steam, OpenCritic, IGDB normalized to 0–100
- **Scheduled jobs** — weekly live leaderboard rebuild; monthly featured sync + snapshot refresh

---

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL 16, Uvicorn |
| Frontend | React 19, Vite, Tailwind CSS v4, Recharts, React Router |
| Data | Steam (no key), OpenCritic via RapidAPI, IGDB via Twitch OAuth |
| Infra | Docker Compose locally; Neon + Render + Vercel in production; GitHub Actions for CI and weekly refresh |

---

## Architecture (hybrid)

```
IGDB catalog search/browse  ──►  live adapters (Steam / OpenCritic / IGDB)  ──►  gap (cached ~1h)
                                        │
                                        ▼
                              leaderboard_cache (top ~50 live gaps)
                                        │
                          monthly sync  ▼
PostgreSQL: Featured Top 10 only  ──►  rating_snapshots (history charts)
```

| Surface | Storage |
|---------|---------|
| Search + most game pages | Live APIs only |
| `/leaderboard/live` | `leaderboard_cache` JSON row |
| `/featured`, snapshot history | `games` (≤10) + `rating_snapshots` |

Jobs:

- `python -m app.jobs.rebuild_live_leaderboard` — weekly (GitHub Actions)
- `python -m app.jobs.sync_featured_top10` — monthly: rotate top 10, delete dropped games, refresh snapshots

IGDB credentials (`IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`) are **required** for catalog search.

---

## Project structure

```
fangap/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/              # settings (.env)
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/v1/
│   │   ├── crud/
│   │   ├── adapters/          # steam, opencritic, igdb
│   │   ├── services/          # normalizer, refresh
│   │   └── jobs/              # refresh_ratings.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # GameCard, ScoreChart, FilterBar
│   │   ├── pages/             # GameList, GameDetail, DivergenceLeaderboard
│   │   ├── api/
│   │   ├── chart/             # day-bucketed critic/fan series
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/workflows/         # ci.yml + refresh.yml
├── docker-compose.yml         # db + app + frontend
├── render.yaml
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.13, Node.js 22, Docker (or Docker Desktop on Windows/WSL)
- Optional API keys: RapidAPI OpenCritic, Twitch app (IGDB). Steam reviews need no key. Seed data includes a short history so charts work without keys.

### Option A — Docker Compose

```bash
cp backend/.env.example backend/.env
# fill OpenCritic / IGDB keys if you have them; DATABASE_URL is overridden in compose
docker compose up --build
```

Then seed once (from the host, with compose `app` running, or exec into the app container):

```bash
docker compose exec app python -m app.seed
```

- API docs: http://localhost:8000/docs
- Frontend (nginx serving the Vite build): http://localhost:5173

If port 5432 is already used by a local Postgres, stop that instance first or change the published port in `docker-compose.yml`.

### Option B — Local processes + Docker Postgres

```bash
docker compose up -d db
```

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend**

```bash
cd frontend
cp .env.example .env            # VITE_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Frontend: http://localhost:5173

### Environment variables

`backend/.env`:

```
DATABASE_URL=postgresql://fangap:fangap@localhost:5432/fangap
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
OPENCRITIC_RAPIDAPI_KEY=
IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
```

`frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

`VITE_*` variables are baked in at **build** time (Vite and the frontend Docker image). Changing the API URL for production means rebuilding the frontend with the Render URL.

### Manual refresh

```bash
cd backend
source venv/bin/activate
python -m app.jobs.rebuild_live_leaderboard
python -m app.jobs.sync_featured_top10
```

Without OpenCritic/IGDB keys those adapters skip; Steam still writes a fan snapshot when `steam_app_id` is set.

---

## API

Interactive docs: http://localhost:8000/docs

| Endpoint | Description |
|---|---|
| `GET /catalog/games` | IGDB search (`q`, `page`, `page_size`) |
| `GET /catalog/games/{igdb_id}/live` | Live multi-source scores + gap (cached) |
| `GET /games/by-igdb/{igdb_id}` | Metadata + live scores + featured link |
| `GET /leaderboard/live` | Cached live divergence top ~50 |
| `GET /games` | Featured Top 10 only (snapshot-backed) |
| `GET /games/{id}/ratings/history` | Featured history for charts |
| `GET /games/divergence/top` | Featured snapshot leaderboard (max 10) |

---

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```

GitHub Actions (`.github/workflows/ci.yml`) runs both suites on every push: backend tests against a Postgres 16 service after `alembic upgrade head`.

---

## Scheduled jobs (GitHub Actions)

- **Weekly** — `.github/workflows/rebuild-leaderboard.yml` runs `rebuild_live_leaderboard` (cached live top ~50).
- **Monthly** — `.github/workflows/refresh.yml` runs `rebuild_live_leaderboard` then `sync_featured_top10` (rotate Featured Top 10, refresh snapshots).

Repo secrets: `DATABASE_URL`, `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET`, optional `OPENCRITIC_RAPIDAPI_KEY`.

---

## Deployment

Accounts are not created by this repo. Provision them, then point the configs at the GitHub repository.

### Known tradeoffs (read these first)

- **Render free web services** sleep after about 15 minutes idle. The first request after that is a slow cold start.
- **Neon free** storage is capped (0.5 GB on the current free tier). Fine for a catalog this size; not for unbounded snapshot history forever.
- **Vercel** builds the `frontend/` app; `VITE_API_URL` must be the **public** Render URL at build time or the browser will still call localhost.

### 1. Database — Neon

1. Create a free Neon project and a database named `fangap`.
2. Copy the pooled or direct `postgresql://…` connection string.
3. From your machine (or CI): set `DATABASE_URL` to that string, run `alembic upgrade head` and `python -m app.seed` once from `backend/`.

### 2. Backend — Render

1. New **Web Service** from this GitHub repo, root directory `backend` (see `render.yaml`).
2. Build: `pip install -r requirements.txt`
3. Start: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment:
   - `DATABASE_URL` — Neon URL
   - `CORS_ORIGINS` — JSON list including your Vercel origin, e.g. `["https://your-app.vercel.app"]`
   - OpenCritic / IGDB keys if you want live critic/IGDB snapshots
5. After the first deploy, copy the `onrender.com` URL.

### 3. Frontend — Vercel

1. New project, **Root Directory** `frontend`.
2. Framework preset: Vite. `vercel.json` rewrites unknown paths to `index.html` (client-side routing).
3. Environment: `VITE_API_URL=https://<your-render-service>.onrender.com` (no trailing slash).
4. Redeploy after changing `VITE_API_URL` so the value is compiled in.

`Done when` the public site loads games from Render/Neon. This repository cannot finish that last click without those accounts.

---

## Roadmap

- User accounts / personal watchlists
- More storefronts (GOG, Epic)
- Alerts when a tracked game’s divergence crosses a threshold

---

## License

[GNU GPL v3](LICENSE)
