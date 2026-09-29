import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchGame, fetchRatingHistory } from '../api/games.js'
import AppHeader from '../components/AppHeader.jsx'
import ScoreChart from '../components/ScoreChart.jsx'

function releaseYear(releaseDate) {
  if (!releaseDate) {
    return null
  }
  return releaseDate.slice(0, 4)
}

function ScoreStat({ label, value, hint }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 px-4 py-3">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="text-2xl font-semibold text-slate-50">
        {value == null ? '—' : Number(value).toFixed(1)}
      </p>
      {hint ? <p className="text-xs text-slate-500">{hint}</p> : null}
    </div>
  )
}

export default function GameDetail() {
  const { gameId } = useParams()
  const [game, setGame] = useState(null)
  const [history, setHistory] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadGame() {
      setStatus('loading')
      setError(null)
      try {
        const [detail, historyPayload] = await Promise.all([
          fetchGame(gameId, { signal: controller.signal }),
          fetchRatingHistory(gameId, { signal: controller.signal }),
        ])
        setGame(detail)
        setHistory(historyPayload.items ?? [])
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
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <main className="mx-auto max-w-3xl space-y-6 px-4 py-10">
        <Link to="/" className="text-sm text-slate-400 hover:text-slate-200">
          ← All games
        </Link>

        {status === 'loading' ? <p className="text-slate-400">Loading game…</p> : null}

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
          <>
            <article className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80">
              {game.cover_url ? (
                <img src={game.cover_url} alt="" className="h-56 w-full object-cover" />
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
                    {game.platforms.map((item) => (
                      <span
                        key={item}
                        className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                ) : null}
                <div className="grid gap-3 sm:grid-cols-3">
                  <ScoreStat label="Critics" value={game.critic_score} hint="Latest critic average" />
                  <ScoreStat label="Players" value={game.fan_score} hint="Latest fan average" />
                  <ScoreStat label="Gap" value={game.divergence} hint="Absolute difference" />
                </div>
              </div>
            </article>

            <section className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
              <h2 className="text-xl font-semibold">Score trend</h2>
              <p className="text-sm text-slate-400">
                Critics in amber, players in blue. The gap between the two lines is FanGap.
              </p>
              <ScoreChart points={history} />
            </section>
          </>
        ) : null}
      </main>
    </div>
  )
}
