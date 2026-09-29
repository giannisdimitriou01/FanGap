# FanGap — Full-Stack Build Plan (Two-Engineer Track)

Backend: FastAPI + PostgreSQL + Docker
Frontend: React (Vite) + Tailwind CSS + Recharts
Sources: Steam, OpenCritic, IGDB
Team: **E1** (some prior experience) and **E2** (new to full-stack / these tools)

---

## Repo layout (monorepo, two top-level folders)

```
fangap/
├── backend/            # FastAPI app (see structure from earlier — unchanged)
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # GameCard, ScoreChart, FilterBar, etc.
│   │   ├── pages/           # GameList, GameDetail, DivergenceLeaderboard
│   │   ├── api/              # fetch wrappers for the backend
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml   # app + db + frontend, three services
└── README.md
```

---

## How to use this plan

Same principle as before, now applied across both stacks: **E2 gets the
clearest, most repetitive tasks first — in both Python and React — so the
concept lands before the complexity does.** E1 owns the pieces with real
design judgment (schema, chart architecture, auth flows, deployment) but
explains reasoning rather than just doing it. Every phase ends in a PR +
review. Pair on the phases marked **Pair** — E2 drives, E1 navigates.

---

## Phase 0 — Project Setup, Both Stacks — **Pair**
- [ ] Create the `fangap` monorepo, initialize git
- [ ] Backend: set up venv, install FastAPI + Uvicorn (as in the earlier guide)
- [ ] Frontend: scaffold with `npm create vite@latest frontend -- --template react`, install Tailwind and Recharts
- [ ] Confirm backend runs on `:8000` and frontend dev server runs on `:5173`, side by side
- [ ] Root `.gitignore` covering both (`venv/`, `node_modules/`, `__pycache__/`, `.env`)

**E2 learning goal:** first exposure to two different tool ecosystems (pip/venv vs npm) in one project, and seeing that they're just two processes running side by side.
**Done when:** both dev servers run locally for both of you, from a clean clone.

---

## Phase 1 — Database Design & Models (backend)
- [ ] **E1**: design the schema (`games`, `rating_snapshots`), explain the reasoning to E2
- [ ] **E2**: implement the SQLAlchemy models
- [ ] **E1**: review
- [ ] Together: initialize Alembic, run first migration against local Postgres

**Done when:** tables exist in Postgres and both of you can insert/query a row manually.

---

## Phase 2 — Vertical Slice: Game List (first full-stack feature)
- [ ] **E2**: build `GET /games` in FastAPI (list endpoint, pagination)
- [ ] **E2**: seed a handful of games manually (via `POST /games` or a small seed script) so there's something to display
- [ ] **E1**: configure CORS on the FastAPI app so the Vite dev server can call it — a small step that quietly breaks a lot of first full-stack attempts if skipped
- [ ] **E2**: build a `GameList` page in React — fetch from `/games`, render as a simple grid/table
- [ ] **E1**: review the frontend-backend contract specifically — do the field names match, is a loading state and an error state handled, not just the happy path

**E2 learning goal:** this is the payoff phase — seeing a database row travel all the way to a rendered browser page for the first time is what makes every later phase make sense.
**Done when:** the running frontend shows real data pulled live from the running backend.

---

## Phase 3 — Game Detail Page & Full CRUD
- [ ] **E2**: add `GET /games/{id}` on the backend
- [ ] **E2**: add React Router, build a `GameDetail` page, link it from `GameList`
- [ ] **E1**: introduce client-side routing concepts, review loading/error states on the new page
- [ ] Optional: add `PATCH`/`DELETE /games/{id}` if you want manual game management

**E2 learning goal:** routing and passing data between pages — the next core React concept after "fetch and render."
**Done when:** clicking a game in the list navigates to its detail page, backed by a real API call.

---

## Phase 4 — External API Adapters (backend) — **Split by difficulty**
- [ ] **E1**: build `opencritic.py` (RapidAPI key auth) and `igdb.py` (Twitch OAuth flow)
- [ ] **E2**: build `steam.py` — no auth, simplest possible integration
- [ ] Together: agree on the shared adapter interface (`base.py`) before splitting
- [ ] Cross-review: E1 reviews E2's adapter; E2 checks E1's adapters against the shared interface contract

**E2 learning goal:** first real third-party API integration, deliberately the easy one.
**Done when:** each adapter runs standalone and returns a clean, predictable shape.

---

## Phase 5 — Normalization & Ingestion Service (backend)
- [ ] **E1**: architect `normalizer.py` and `refresh.py` — the piece tying adapters + DB together
- [ ] **E2**: write tests for the normalization logic once it exists
- [ ] **E1**: walk E2 through the full data flow

**E2 learning goal:** writing meaningful unit tests against logic that's already concrete.
**Done when:** running refresh for one game populates snapshot rows from all 3 sources, with tests passing.

---

## Phase 6 — Historical Tracking & Divergence (full-stack, the hero feature)
- [ ] **E2**: build backend endpoints — `/games/{id}/ratings`, `/ratings/history`, `/divergence`, `/divergence/top`
- [ ] **E1**: architect the `ScoreChart` component (Recharts line chart) and the `DivergenceLeaderboard` page — this is the feature that makes FanGap's CV pitch land, so give it real design attention
- [ ] **E2**: implement the chart component with E1 pairing, wiring it to the history endpoint
- [ ] **E1**: review — focus on what the chart communicates at a glance, not just whether it renders

**E2 learning goal:** first exposure to a charting library and shaping API responses specifically for visualization needs.
**Done when:** a game's detail page shows its score trend over time, and there's a working leaderboard of most-divergent games.

---

## Phase 7 — Search & Filtering (full-stack)
- [ ] **E2**: add query params to `GET /games` (genre, platform, sort by divergence)
- [ ] **E2**: build a `FilterBar` component and wire it to the query params
- [ ] **E1**: review for debouncing the search input and keeping filter state in the URL (so a filtered view is shareable/bookmarkable)

**Done when:** you can search/filter the game list and the results update without a full page reload.

---

## Phase 8 — Scheduled Refresh Job (backend/devops)
- [ ] **E1**: build `refresh_ratings.py` and the GitHub Actions cron workflow
- [ ] **E2**: shadow actively, then write the README section explaining what it does and why
- [ ] Confirm the scheduled run reaches the deployed database via GitHub secrets

**E2 learning goal:** exposure to CI/CD and scheduled jobs, via narrating + documenting rather than owning the implementation.
**Done when:** a scheduled run adds new snapshot rows with no manual steps.

---

## Phase 9 — Dockerization, Both Stacks — **Pair**
- [ ] **E1**: explain what Docker solves here (environment parity across both stacks)
- [ ] **E2**: write the backend `Dockerfile` (from the earlier plan)
- [ ] **E2**: write the frontend `Dockerfile` (multi-stage: `npm run build`, then serve the static output, e.g. via nginx)
- [ ] Together: write `docker-compose.yml` with three services — `app`, `db`, `frontend`
- [ ] **E1**: review, focusing on why each instruction is there

**E2 learning goal:** Docker fundamentals, now across two different types of app (a Python process vs. a static build served by nginx) — a good "aha" moment on what containers actually abstract away.
**Done when:** `docker compose up` gives a fully working stack — backend, db, and frontend — for both of you, from a clean clone.

---

## Phase 10 — Testing, Both Stacks
- [ ] **E2**: backend endpoint tests (pytest) + frontend component tests (Vitest + React Testing Library) for `GameList`/`GameDetail`
- [ ] **E1**: adapter/service tests + a test for the `ScoreChart` component's data handling
- [ ] Cross-review: each of you reviews the other's tests, asking "what case isn't covered here?"
- [ ] GitHub Actions workflow runs both test suites on every push

**Done when:** `pytest` and the frontend test suite both pass in CI on every push.

---

## Phase 11 — Deployment, Full Stack
- [ ] Database: create a free **Neon** Postgres project
- [ ] Backend: deploy to **Render** (free web service) connected to the GitHub repo
- [ ] Frontend: deploy to **Vercel** (Hobby tier), pointed at the `frontend/` subfolder
- [ ] **E1** leads; **E2** shadows and writes the "Deployment" section of the README step by step
- [ ] Note the known tradeoffs in the README: Render's free tier sleeps after ~15 minutes idle (first request after that is slow), and Neon's free tier caps storage at 0.5GB — fine for a portfolio project, worth stating explicitly rather than being surprised by it later

**E2 learning goal:** understanding what "deploying a full-stack app" actually involves end-to-end, documented in your own words.
**Done when:** FanGap is publicly reachable — frontend talking to the live backend talking to the live database.

---

## Phase 12 — Documentation & Polish
- [ ] **E2**: write the main `README.md` (what FanGap does, how to run both stacks locally, screenshots)
- [ ] **E1**: add the "Architecture & Design Decisions" section (why Postgres over SQLite, why snapshots, why this adapter pattern, why Recharts) — CV/interview gold for both of you
- [ ] Both: clean up FastAPI's auto-docs, add descriptions/examples
- [ ] Both: final walkthrough — E2 explains the whole system back to E1, frontend and backend, end to end

**Done when:** someone unfamiliar with FanGap could clone the repo and run the whole thing from the README alone — and E2 can explain how every layer connects, not just the parts they wrote.
