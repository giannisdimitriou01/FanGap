import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { fetchTopDivergence } from '../api/games.js'
import AppHeader from '../components/AppHeader.jsx'

export default function DivergenceLeaderboard() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      setStatus('loading')
      setError(null)
      try {
        const data = await fetchTopDivergence({ signal: controller.signal })
        setItems(data.items ?? [])
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
          <h1 className="text-3xl font-bold tracking-tight">Divergence leaderboard</h1>
          <p className="text-slate-400">
            Games where critics and players disagree the most, based on the latest snapshot
            from each source.
          </p>
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
          <p className="text-slate-400">
            No divergence yet. Seed history or refresh ratings so both critic and fan scores exist.
          </p>
        ) : null}

        {status === 'ok' && items.length > 0 ? (
          <ol className="space-y-3">
            {items.map((row, index) => (
              <li key={row.game_id}>
                <Link
                  to={`/games/${row.game_id}`}
                  className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-4 hover:border-slate-600"
                >
                  <span className="w-8 text-center text-lg font-semibold text-slate-500">
                    {index + 1}
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
