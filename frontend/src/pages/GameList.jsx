import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { searchCatalog } from '../api/catalog.js'
import AppHeader from '../components/AppHeader.jsx'
import GameCard from '../components/GameCard.jsx'

const PAGE_SIZE = 20

function useDebouncedValue(value, delayMs) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])
  return debounced
}

export default function GameList() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const page = Math.max(1, Number(params.get('page') || '1') || 1)
  const debouncedQ = useDebouncedValue(q, 300)

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
        const data = await searchCatalog({
          page,
          pageSize: PAGE_SIZE,
          q: debouncedQ,
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
  }, [page, debouncedQ, reloadToken])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  function updateSearch(value) {
    const next = new URLSearchParams(params)
    if (value) {
      next.set('q', value)
    } else {
      next.delete('q')
    }
    next.delete('page')
    setParams(next)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <main className="mx-auto max-w-6xl space-y-8 px-4 py-10">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Search games</h1>
          <p className="text-slate-400">
            Browse IGDB. Live critic vs player scores on each game. Monthly history only for the
            Featured Top 10.
          </p>
        </header>

        <label className="block max-w-xl text-sm">
          <span className="mb-1 block text-slate-400">Search</span>
          <input
            type="search"
            value={q}
            onChange={(event) => updateSearch(event.target.value)}
            placeholder="Game title"
            className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          />
        </label>

        {status === 'loading' ? <p className="text-slate-400">Loading games…</p> : null}

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
          <p className="text-slate-400">No games match that search.</p>
        ) : null}

        {status === 'ok' && items.length > 0 ? (
          <>
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((game) => (
                <GameCard key={game.igdb_id} game={game} />
              ))}
            </div>
            {totalPages > 1 ? (
              <div className="flex items-center justify-between text-sm text-slate-400">
                <button
                  type="button"
                  disabled={page <= 1}
                  className="rounded-md border border-slate-700 px-3 py-1.5 disabled:opacity-40"
                  onClick={() => {
                    const next = new URLSearchParams(params)
                    next.set('page', String(page - 1))
                    setParams(next)
                  }}
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
                  onClick={() => {
                    const next = new URLSearchParams(params)
                    next.set('page', String(page + 1))
                    setParams(next)
                  }}
                >
                  Next
                </button>
              </div>
            ) : null}
          </>
        ) : null}
      </main>
    </div>
  )
}
