# FanGap

**Comparing what critics say versus what players actually feel — and tracking how that gap changes over time.**

FanGap aggregates video game ratings from Steam, OpenCritic, and IGDB onto a shared 0–100 scale. It stores every fetch as a new snapshot (never an overwrite), so you can chart critic vs player scores after launch and rank the games where those audiences disagree most.

![Game list with search and filters](docs/screenshots/games.png)

![Score trend on a game detail page](docs/screenshots/detail.png)

![Divergence leaderboard](docs/screenshots/leaderboard.png)

---

## Features

- **Critic vs. fan divergence** — latest critic average vs latest fan average per game, ranked by absolute gap
- **Historical rating tracking** — `rating_snapshots` appends a row per source/audience/run
- **Multi-source aggregation** — Steam store reviews, OpenCritic Top Critic Score, IGDB critic + user ratings
- **Search and filtering** — title search, genre, platform, sort by title or divergence; filter state lives in the URL
- **Scheduled refresh** — GitHub Actions cron writes new snapshots against the deployed database

---

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL 16, Uvicorn |
| Frontend | React 19, Vite, Tailwind CSS v4, Recharts, React Router |
| Data | Steam (no key), OpenCritic via RapidAPI, IGDB via Twitch OAuth |
| Infra | Docker Compose locally; Neon + Render + Vercel in production; GitHub Actions for CI and weekly refresh |

---

## Architecture

```
Steam / OpenCritic / IGDB
        │
        ▼
   adapters/            one module per source, shared RawRating interface
        │
        ▼
   normalizer.py        maps each source onto 0–100
        │
        ▼
   refresh.py           appends rating_snapshots (never updates an old row)
        │
        ▼
   PostgreSQL           games + rating_snapshots
        │
        ▼
   FastAPI              /games, history, /games/divergence/top
        │
        ▼
   React                list, FilterBar, ScoreChart, leaderboard
```

A Monday 06:00 UTC GitHub Actions workflow runs `python -m app.jobs.refresh_ratings`. That job needs `DATABASE_URL` (and optional OpenCritic/IGDB secrets) so it writes into the **deployed** database, not a GitHub runner’s empty disk.

### Design decisions

- **PostgreSQL over SQLite** — free PaaS filesystems are ephemeral. A file database would vanish on every Render deploy. Postgres (local Docker or Neon) is the same engine in both places.
- **Snapshots over overwrites** — a single `current_score` column cannot answer “how did this look six months after launch?” Each successful adapter fetch inserts a new `rating_snapshots` row with `fetched_at`.
- **Source + audience** — Steam is fan-only, OpenCritic is critic-only, IGDB returns both. Divergence averages the *latest* snapshot per `(game, source, audience)`, then takes `abs(avg critics − avg fans)`. Games need at least one critic and one fan sample to appear on the leaderboard.
- **Adapters behind one interface** — `fetch_ratings(GameRef) -> list[RawRating]`. Adding GOG later should not touch FastAPI routes or the chart.
- **Recharts** — small dependency, SVG line chart, enough for two series (critics amber, players blue) without a heavy dashboard kit.
- **Filter state in the URL** — `?q=&genre=&platform=&sort=` is shareable and survives refresh. Search input is debounced 300ms so every keystroke does not hit Postgres.

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
python -m app.jobs.refresh_ratings          # all games
python -m app.services.refresh 1            # one game id
```

Without OpenCritic/IGDB keys those adapters skip; Steam still writes a fan snapshot when `steam_app_id` is set.

---

## API

Interactive docs: http://localhost:8000/docs

| Endpoint | Description |
|---|---|
| `GET /games` | Paginated list. Query: `q`, `genre`, `platform`, `sort=title\|divergence`, `page`, `page_size` |
| `GET /games/{id}` | Detail plus latest critic/fan averages and divergence |
| `POST /games` | Create |
| `PATCH /games/{id}` | Partial update |
| `DELETE /games/{id}` | Delete (cascades snapshots) |
| `GET /games/{id}/ratings` | Latest snapshot per source + audience |
| `GET /games/{id}/ratings/history` | Full history, oldest first (chart input) |
| `GET /games/{id}/divergence` | Gap for one game |
| `GET /games/divergence/top` | Leaderboard |

---

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```

GitHub Actions (`.github/workflows/ci.yml`) runs both suites on every push: backend tests against a Postgres 16 service after `alembic upgrade head`.

---

## Scheduled refresh (GitHub Actions)

`.github/workflows/refresh.yml` runs weekly (`0 6 * * 1`) and on `workflow_dispatch`.

**Why a GitHub cron instead of a process on the API box?** Render’s free web service sleeps. A runner that boots, writes snapshots, and exits does not need a always-on worker.

Repo secrets (Settings → Secrets and variables → Actions):

| Secret | Purpose |
|---|---|
| `DATABASE_URL` | Neon (or other hosted) connection string the job should write to |
| `OPENCRITIC_RAPIDAPI_KEY` | Optional; skipped if empty |
| `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET` | Optional Twitch credentials for IGDB |

Until those secrets exist, the workflow file is in the repo but cannot reach a hosted database. After deploy, run it once with **Run workflow** and confirm new `rating_snapshots` rows in Neon.

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
