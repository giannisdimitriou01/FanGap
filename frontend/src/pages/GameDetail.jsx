import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchGame } from '../api/games.js'

function releaseYear(releaseDate) {
  if (!releaseDate) {
    return null
  }
  return releaseDate.slice(0, 4)
}

export default function GameDetail() {
  const { gameId } = useParams()
  const [game, setGame] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadGame() {
      setStatus('loading')
      setError(null)
      try {
        const data = await fetchGame(gameId, { signal: controller.signal })
        setGame(data)
        setStatus('ok')
      } catch (err) {
        if (err.name === 'AbortError') {
          return
        }
        setGame(null)
        setError(err.message || 'Could not load this game.')
        setStatus(err.status === 404 ? 'notfound' : 'error')
      }
    }

    loadGame()
    return () => controller.abort()
  }, [gameId, reloadToken])

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-slate-100">
      <div className="mx-auto max-w-3xl space-y-6">
        <Link to="/" className="text-sm text-slate-400 hover:text-slate-200">
          ← All games
        </Link>

        {status === 'loading' ? (
          <p className="text-slate-400">Loading game…</p>
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

        {status === 'notfound' ? (
          <p className="text-slate-400">That game was not found.</p>
        ) : null}

        {status === 'ok' && game ? (
          <article className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80">
            {game.cover_url ? (
              <img
                src={game.cover_url}
                alt=""
                className="h-56 w-full object-cover"
              />
            ) : null}
            <div className="space-y-4 p-6">
              <header>
                <h1 className="text-3xl font-bold tracking-tight">{game.title}</h1>
                {releaseYear(game.release_date) ? (
                  <p className="text-slate-400">{releaseYear(game.release_date)}</p>
                ) : null}
              </header>
              {game.genres.length > 0 ? (
                <p className="text-slate-300">{game.genres.join(' · ')}</p>
              ) : null}
              {game.platforms.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {game.platforms.map((platform) => (
                    <span
                      key={platform}
                      className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300"
                    >
                      {platform}
                    </span>
                  ))}
                </div>
              ) : null}
              <dl className="grid gap-2 text-sm text-slate-400 sm:grid-cols-3">
                <div>
                  <dt className="uppercase tracking-wide">Steam</dt>
                  <dd className="text-slate-200">{game.steam_app_id ?? '—'}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide">OpenCritic</dt>
                  <dd className="text-slate-200">{game.opencritic_id ?? '—'}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide">IGDB</dt>
                  <dd className="text-slate-200">{game.igdb_id ?? '—'}</dd>
                </div>
              </dl>
            </div>
          </article>
        ) : null}
      </div>
    </main>
  )
}
