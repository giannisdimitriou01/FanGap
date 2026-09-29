# FanGap — Backend Build Plan (Two-Engineer Track)

Stack: FastAPI + PostgreSQL + Dockerddddddd
Sources: Steam, OpenCritic, IGDB
Team: **E1** (some prior experience) and **E2** (new to full-stack / these tools)

---

## How to use this plan

The phases are the same shape as a solo plan, but each one now carries role
assignments and a learning goal. The underlying idea:

- **E2 starts on low-ambiguity, high-repetition tasks** (CRUD endpoints, the
  simplest adapter, writing tests for code they already understand) — these
  build real confidence with the tools fast, without needing architectural
  judgment calls yet.
- **E1 owns the tasks with more ambiguity** (schema design, harder auth
  flows, deployment, service architecture) — but explains *why*, not just
  *what*, so E1 is also leveling up by having to articulate reasoning, not
  just execute.
- **Every phase ends with a PR + review**, ideally E1 reviewing E2's code
  with comments that explain the "why" behind requested changes, not just
  "fix this." That review is where most of E2's actual learning happens.
- **Pair on the phases marked "Pair"** — sit together, E2 drives (types),
  E1 navigates (explains). This is the fastest way to transfer tool
  familiarity (git, terminal, VSCode, Docker) without E2 feeling lost.
- Track phases as milestones on a shared GitHub Project board so both of you
  can see who owns what and where the bottlenecks are.

---

## Phase 0 — Project Setup & Environment — **Pair**
- [ ] Create the FanGap repo, initialize git, agree on branch strategy (e.g. `main` + feature branches + PRs)
- [ ] Set up virtual environment, install FastAPI + Uvicorn — E2 drives, E1 explains what each tool does
- [ ] Create the file structure together
- [ ] Set up `.env.example` and `.gitignore`
- [ ] Confirm `uvicorn app.main:app --reload` runs and `/docs` loads

**E2 learning goal:** get comfortable with venvs, git basics, and the terminal — this phase is the foundation for everything else, so don't rush it.
**Done when:** empty FastAPI app runs locally for both of you, from a clean clone.

---

## Phase 1 — Database Design & Models
- [ ] **E1**: design the schema (`games`, `rating_snapshots`) and walk E2 through the reasoning — why a snapshots table instead of overwriting scores, why these fields
- [ ] **E2**: implement the SQLAlchemy models in `app/models/` based on E1's design
- [ ] **E1**: review — explain any relationship/foreign key issues, not just fix them
- [ ] Together: initialize Alembic, generate first migration, run it against local Postgres

**E2 learning goal:** first real exposure to ORMs and how a schema maps to code.
**E1 stretch:** practice explaining a design decision clearly enough that E2 could defend it later.
**Done when:** tables exist in Postgres and both of you can insert/query a row manually.

---

## Phase 2 — Core API Skeleton
- [ ] **E2**: build the basic CRUD endpoints for `games` (`GET /games`, `GET /games/{id}`, `POST /games`) — this is the best first "real feature" for learning FastAPI end-to-end
- [ ] **E2**: add `GET /health`
- [ ] **E1**: review PR — focus feedback on pagination, error handling (404s), and response models, since these patterns get reused everywhere later
- [ ] **E1**: pair briefly on Pydantic schemas if E2 gets stuck on request/response typing

**E2 learning goal:** the full request → route → CRUD → DB → response loop, in the tool you'll use for every endpoint after this.
**Done when:** E2 can create and fetch games through Swagger UI, unassisted.

---

## Phase 3 — External API Adapters — **Split by difficulty**
- [ ] **E1**: build `opencritic.py` (RapidAPI key auth) and `igdb.py` (Twitch OAuth token flow) — the two adapters with real auth complexity
- [ ] **E2**: build `steam.py` — no auth needed, simplest possible integration, a good first "talk to an external API" task
- [ ] Together: agree on the shared adapter interface in `base.py` *before* splitting, so both adapters return the same shape
- [ ] **E1**: review E2's adapter; **E2** reviews E1's adapters for the interface contract (even without understanding OAuth internals, checking "does it return what base.py expects" is a legitimate review)

**E2 learning goal:** first taste of calling a third-party API and handling its response — deliberately the easy one, so the concept lands before the complexity does.
**E1 stretch:** handling OAuth token refresh and rate-limit-aware retries — good real-world experience.
**Done when:** each adapter runs standalone and returns a clean, predictable shape.

---

## Phase 4 — Normalization & Ingestion Service
- [ ] **E1**: architect `app/services/normalizer.py` and `refresh.py` — this is the piece that ties adapters + DB together and has the most design judgment involved
- [ ] **E2**: write tests for the normalization logic once it exists (given raw scores in, expected normalized scores out) — a very approachable entry into testing
- [ ] **E1**: walk E2 through the service once built, so E2 understands the full data flow, not just the tests

**E2 learning goal:** how to write meaningful unit tests, using logic that's already concrete and easy to reason about.
**E1 stretch:** service-layer architecture — keeping business logic out of route handlers, a pattern worth being able to justify in interviews.
**Done when:** running refresh for one game populates snapshot rows from all 3 sources, with tests passing.

---

## Phase 5 — Historical Tracking Endpoints
- [ ] **E2**: build `/games/{id}/ratings`, `/games/{id}/ratings/history`, `/games/{id}/divergence`, `/games/divergence/top` — direct reuse of CRUD patterns from Phase 2
- [ ] **E1**: review specifically for query efficiency (N+1 queries, missing indexes) — a concrete, teachable performance lesson
- [ ] **E1**: add a DB index where needed and explain why, rather than just adding it silently

**E2 learning goal:** reinforcing FastAPI/SQLAlchemy patterns on slightly more complex queries (joins, aggregation for divergence).
**Done when:** endpoints return real data ready for the frontend to plot.

---

## Phase 6 — Scheduled Refresh Job
- [ ] **E1**: build `app/jobs/refresh_ratings.py` and the GitHub Actions cron workflow
- [ ] **E2**: shadow this one actively — ask E1 to narrate while setting it up, then have E2 write the workflow's README section explaining what it does and why
- [ ] Confirm the scheduled run reaches the deployed database using GitHub secrets

**E2 learning goal:** exposure to CI/CD concepts and scheduled jobs, even without owning the implementation yet — this is a "watch and document" phase, not a "hands off" phase.
**Done when:** a scheduled run adds snapshot rows with no manual steps.

---

## Phase 7 — Dockerization — **Pair**
- [ ] **E1**: explain what Docker is solving here (environment parity) before writing anything
- [ ] **E2**: write the `Dockerfile` and `docker-compose.yml` with E1 guiding
- [ ] **E1**: review, focusing on why each instruction is there (layer caching, `.dockerignore`, etc.)

**E2 learning goal:** Docker fundamentals — a tool E2 has "no experience" with, so this phase deliberately stays hands-on and paired rather than delegated.
**Done when:** `docker compose up` gives a working stack for both of you, from a clean clone.

---

## Phase 8 — Testing
- [ ] **E2**: write tests for the endpoints they built (Phases 2 and 5)
- [ ] **E1**: write tests for the adapters and services (mocking external HTTP calls)
- [ ] Cross-review: each of you reviews the other's tests, asking "what case isn't covered here?"
- [ ] Add a GitHub Actions workflow to run tests on every push

**Done when:** `pytest` passes in CI on every push, covering both of your areas.

---

## Phase 9 — Deployment
- [ ] **E1**: lead deployment (Neon Postgres + Railway/Render + env/secret configuration) — infra experience worth having
- [ ] **E2**: shadow and write the "Deployment" section of the README as you go, step by step, as if teaching the next person
- [ ] Together: verify `/docs` and a couple of real endpoints work on the live URL

**E2 learning goal:** understanding what "deploying a backend" actually involves end-to-end, documented in your own words.
**Done when:** FanGap's backend is publicly reachable and serving real data.

---

## Phase 10 — Documentation & Polish
- [ ] **E2**: write the main `README.md` (what FanGap does, how to run it locally) — good writing/communication practice
- [ ] **E1**: review and add the "Architecture & Design Decisions" section (why Postgres over SQLite, why snapshots, why this adapter pattern) — this section is CV/interview gold for both of you
- [ ] Both: clean up FastAPI's auto-docs — add descriptions/examples to endpoints and schemas
- [ ] Both: do a final walkthrough together — E2 explains the whole system back to E1, end to end

**Done when:** someone unfamiliar with FanGap could clone the repo and get it running from the README alone — and E2 can explain how the whole thing works, not just the parts they wrote.
