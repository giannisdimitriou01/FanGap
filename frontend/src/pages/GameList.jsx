import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { fetchGames } from '../api/games.js'
import AppHeader from '../components/AppHeader.jsx'
import FilterBar from '../components/FilterBar.jsx'
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
  const genre = params.get('genre') ?? ''
  const platform = params.get('platform') ?? ''
  const sort = params.get('sort') === 'divergence' ? 'divergence' : 'title'
  const page = Math.max(1, Number(params.get('page') || '1') || 1)
  const debouncedQ = useDebouncedValue(q, 300)

  const [reloadToken, setReloadToken] = useState(0)
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [genres, setGenres] = useState([])
  const [platforms, setPlatforms] = useState([])
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
          q: debouncedQ,
          genre,
          platform,
          sort,
          signal: controller.signal,
        })
        setItems(data.items)
        setTotal(data.total)
        setGenres(data.genres ?? [])
        setPlatforms(data.platforms ?? [])
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
  }, [page, debouncedQ, genre, platform, sort, reloadToken])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  function updateFilters(patch) {
    const next = new URLSearchParams(params)
    Object.entries(patch).forEach(([key, value]) => {
      if (value) {
        next.set(key, value)
      } else {
        next.delete(key)
      }
    })
    next.delete('page')
    setParams(next)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <main className="mx-auto max-w-6xl space-y-8 px-4 py-10">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Games</h1>
          <p className="text-slate-400">
            Critic scores vs player scores — and how that gap changes over time.
          </p>
        </header>

        <FilterBar
          q={q}
          genre={genre}
          platform={platform}
          sort={sort}
          genres={genres}
          platforms={platforms}
          onChange={updateFilters}
        />

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
          <p className="text-slate-400">No games match those filters.</p>
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
