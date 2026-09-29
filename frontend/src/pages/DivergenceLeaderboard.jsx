import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { fetchLiveLeaderboard } from '../api/leaderboard.js'
import AppHeader from '../components/AppHeader.jsx'

export default function DivergenceLeaderboard() {
  const [items, setItems] = useState([])
  const [meta, setMeta] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      setStatus('loading')
      setError(null)
      try {
        const data = await fetchLiveLeaderboard({ signal: controller.signal })
        setItems(data.items ?? [])
        setMeta(data)
        setStatus('ok')
      } catch (err) {
        if (err.name === 'AbortError') {
          return
        }
        setError(err.message || 'Could not load the leaderboard.')
        setStatus('error')
      }
    }

    load()
    return () => controller.abort()
  }, [reloadToken])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <main className="mx-auto max-w-4xl space-y-8 px-4 py-10">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Live divergence leaderboard</h1>
          <p className="text-slate-400">
            Cached ranking from IGDB popular titles with live multi-source scores. Featured Top 10
            entries also keep monthly snapshot history.
          </p>
          {meta?.message ? <p className="text-sm text-amber-300">{meta.message}</p> : null}
        </header>

        {status === 'loading' ? <p className="text-slate-400">Loading leaderboard…</p> : null}

        {status === 'error' ? (
          <div className="space-y-3 rounded-lg border border-red-900/60 bg-red-950/40 p-4">
            <p className="text-red-200">{error}</p>
            <button
              type="button"
              className="rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-900"
              onClick={() => setReloadToken((token) => token + 1)}
            >
              Retry
            </button>
          </div>
        ) : null}

        {status === 'ok' && items.length === 0 ? (
          <p className="text-slate-400">No live leaderboard yet. Run rebuild_live_leaderboard on the backend.</p>
        ) : null}

        {status === 'ok' && items.length > 0 ? (
          <ol className="space-y-3">
            {items.map((row) => (
              <li key={row.igdb_id}>
                <Link
                  to={`/games/igdb/${row.igdb_id}`}
                  className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-4 hover:border-slate-600"
                >
                  <span className="w-8 text-center text-lg font-semibold text-slate-500">
                    {row.rank}
                  </span>
                  {row.cover_url ? (
                    <img src={row.cover_url} alt="" className="h-14 w-24 rounded object-cover" />
                  ) : null}
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-semibold">{row.title}</p>
                    <p className="text-sm text-slate-400">
                      Critics {Number(row.critic_score).toFixed(1)} · Players{' '}
                      {Number(row.fan_score).toFixed(1)}
                    </p>
                    {row.featured_game_id ? (
                      <p className="text-xs text-sky-300">Featured · monthly history</p>
                    ) : null}
                  </div>
                  <p className="text-xl font-semibold text-amber-300">
                    {Number(row.divergence).toFixed(1)}
                  </p>
                </Link>
              </li>
            ))}
          </ol>
        ) : null}
      </main>
    </div>
  )
}
