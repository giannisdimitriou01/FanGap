# FanGap hybrid architecture

## User-facing split

| Question | Answer |
|----------|--------|
| Browse many games? | Yes — IGDB search (`GET /catalog/games`) |
| Live critic vs fan on any game? | Yes — `GET /catalog/games/{igdb_id}/live` or `GET /games/by-igdb/{igdb_id}` |
| History chart for every game? | No — only Featured Top 10 |
| What happens when a game leaves the top 10? | Row + all snapshots deleted from Postgres |

## Backend routes

- **Catalog:** `/catalog/games`, `/catalog/games/{igdb_id}`, `/catalog/games/{igdb_id}/live`
- **Live leaderboard:** `/leaderboard/live`
- **Featured:** `/games` (≤10), `/games/{id}/ratings/history`, `/games/divergence/top`

## Jobs

1. `rebuild_live_leaderboard` — scores IGDB pool with live adapters, stores top 50 in `leaderboard_cache`
2. `sync_featured_top10` — takes top 10 from cache, rotates `games`, runs `refresh_game` for snapshots

Set `SEED_FEATURED=1` locally for one demo featured game with fake history without running sync.
