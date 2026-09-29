import { useEffect, useState } from 'react'

import { fetchGames } from '../api/games.js'
import GameCard from '../components/GameCard.jsx'

const PAGE_SIZE = 20

export default function GameList() {
  const [page, setPage] = useState(1)
  const [reloadToken, setReloadToken] = useState(0)
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadGames() {
      setStatus('loading')
      setError(null)
      try {
        const data = await fetchGames({
          page,
          pageSize: PAGE_SIZE,
          signal: controller.signal,
        })
        setItems(data.items)
        setTotal(data.total)
        setStatus('ok')
      } catch (err) {
        if (err.name === 'AbortError') {
          return
        }
        setError(err.message || 'Could not load games.')
        setStatus('error')
      }
    }

    loadGames()
    return () => controller.abort()
  }, [page, reloadToken])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">FanGap</h1>
          <p className="text-slate-400">
            Critic scores vs player scores — and how that gap changes over time.
          </p>
        </header>

        {status === 'loading' ? (
          <p className="text-slate-400">Loading games…</p>
        ) : null}

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
          <p className="text-slate-400">No games yet. Seed the database and refresh.</p>
        ) : null}

        {status === 'ok' && items.length > 0 ? (
          <>
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((game) => (
                <GameCard key={game.id} game={game} />
              ))}
            </div>
            {totalPages > 1 ? (
              <div className="flex items-center justify-between text-sm text-slate-400">
                <button
                  type="button"
                  disabled={page <= 1}
                  className="rounded-md border border-slate-700 px-3 py-1.5 disabled:opacity-40"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                >
                  Previous
                </button>
                <span>
                  Page {page} of {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  className="rounded-md border border-slate-700 px-3 py-1.5 disabled:opacity-40"
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </main>
  )
}
