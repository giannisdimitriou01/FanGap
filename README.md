# FanGap

**Comparing what critics say versus what players actually feel — and tracking how that gap changes over time.**

FanGap aggregates video game ratings from critics and fans across multiple sources, highlights where the two disagree most, and tracks how sentiment shifts over the months and years after a game's release.

---

## Features

- **Critic vs. fan divergence** — surfaces games where critic scores and player scores disagree the most
- **Historical rating tracking** — scores are stored as time-stamped snapshots, not overwritten, so you can chart how a game's reception changes over time
- **Multi-source aggregation** — pulls and normalizes ratings from Steam, OpenCritic, and IGDB onto a common 0–100 scale
- **Search and filtering** — browse games by genre, platform, or divergence score
- **Automated refresh** — a scheduled job keeps ratings up to date without manual intervention

---

## Tech Stack

**Backend**
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic (models & migrations)
- Pydantic (request/response validation)
- Docker

**Frontend**
- React (Vite)
- Tailwind CSS
- Recharts (score trend charts, divergence leaderboard)

**Data Sources**
- [Steam](https://partner.steamgames.com/doc/store/getreviews) — fan/user review scores
- OpenCritic (via RapidAPI) — critic scores
- [IGDB](https://api-docs.igdb.com/) — both critic (`aggregated_rating`) and user (`rating`) scores

**Infrastructure**
- Neon — hosted PostgreSQL
- Render — backend hosting
- Vercel — frontend hosting
- GitHub Actions — scheduled rating refresh + CI

---

## Architecture

```
Steam / OpenCritic / IGDB
        │
        ▼
   adapters/           (one module per source, shared interface)
        │
        ▼
   normalizer.py        (maps each source's score to a 0–100 scale)
        │
        ▼
   refresh.py            (writes a new rating_snapshots row per source, per run)
        │
        ▼
   PostgreSQL            (games, rating_snapshots)
        │
        ▼
   FastAPI endpoints      (/games, /games/{id}/ratings/history, /divergence)
        │
        ▼
   React frontend          (game list, detail page with trend chart, leaderboard)
```

A scheduled GitHub Actions job runs `refresh.py` periodically, so rating history accumulates automatically over time.

---

## Project Structure

```
fangap/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config, settings
│   │   ├── db/               # engine, session
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/v1/            # route handlers
│   │   ├── crud/               # DB operations
│   │   ├── adapters/            # steam.py, opencritic.py, igdb.py
│   │   ├── services/             # normalizer.py, refresh.py
│   │   └── jobs/                  # refresh_ratings.py (cron entrypoint)
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # GameCard, ScoreChart, FilterBar
│   │   ├── pages/             # GameList, GameDetail, DivergenceLeaderboard
│   │   ├── api/                 # fetch wrappers for the backend
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (recommended, simplest path)
- API credentials: a RapidAPI key for OpenCritic, and a Twitch developer app for IGDB (Steam's review endpoint needs no key)

### Option A — Docker (recommended)

```bash
git clone <your-repo-url>
cd fangap
cp backend/.env.example backend/.env   # fill in your API keys and DB URL
docker compose up
```

This starts the backend, frontend, and a local Postgres instance together.

- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

### Option B — Manual setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # fill in your values
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Set these in `backend/.env` (see `.env.example`):

```
DATABASE_URL=postgresql://user:password@localhost:5432/fangap
OPENCRITIC_RAPIDAPI_KEY=your_key_here
IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
```

---

## API Documentation

Once the backend is running, interactive API docs (Swagger UI) are available at:
```
http://localhost:8000/docs
```

Key endpoints:
| Endpoint | Description |
|---|---|
| `GET /games` | List games (supports search/filter query params) |
| `GET /games/{id}` | Game detail |
| `GET /games/{id}/ratings` | Latest score per source |
| `GET /games/{id}/ratings/history` | Full rating history (for trend charts) |
| `GET /games/divergence/top` | Leaderboard of most critic/fan-divergent games |

---

## Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

---

## Deployment

| Component | Service | Notes |
|---|---|---|
| Database | Neon | Free tier: 0.5GB storage cap |
| Backend | Render | Free tier: spins down after ~15 min idle (cold start on first request) |
| Frontend | Vercel | Free (Hobby) tier |
| Scheduled refresh | GitHub Actions | Cron job, runs `refresh_ratings.py` |

---

## Design Decisions

- **PostgreSQL over SQLite** — most free hosting platforms use ephemeral filesystems, so a file-based DB would be wiped on redeploy
- **Snapshot table over overwriting scores** — `rating_snapshots` stores one row per fetch rather than updating a single "current score" field, which is what makes historical trend tracking possible
- **Separate adapter per source** — each external API (Steam, OpenCritic, IGDB) has its own module behind a shared interface, so adding or replacing a source later doesn't touch the rest of the app

---

## Roadmap

- [ ] User accounts / personal watchlists
- [ ] Support for additional platforms (e.g. GOG, Epic)
- [ ] Notifications when a tracked game's divergence crosses a threshold

---

## Contributors

Built by two engineers as a full-stack learning and portfolio project.

---

## License

*(Choose a license — MIT is a common default for portfolio projects.)*
