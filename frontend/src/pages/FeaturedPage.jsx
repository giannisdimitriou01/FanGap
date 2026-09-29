import { useEffect, useState } from 'react'

import { fetchFeaturedGames } from '../api/featured.js'
import AppHeader from '../components/AppHeader.jsx'
import GameCard from '../components/GameCard.jsx'

export default function FeaturedPage() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    fetchFeaturedGames({ signal: controller.signal })
      .then((data) => {
        setItems(data.items ?? [])
        setStatus('ok')
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          setError(err.message)
          setStatus('error')
        }
      })
    return () => controller.abort()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <main className="mx-auto max-w-6xl space-y-8 px-4 py-10">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Featured Top 10</h1>
          <p className="text-slate-400">
            These games keep monthly snapshot history and rotate based on live divergence.
          </p>
        </header>
        {status === 'loading' ? <p className="text-slate-400">Loading…</p> : null}
        {status === 'error' ? <p className="text-red-300">{error}</p> : null}
        {status === 'ok' && items.length === 0 ? (
          <p className="text-slate-400">No featured games yet. Run sync_featured_top10 on the backend.</p>
        ) : null}
        {status === 'ok' && items.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        ) : null}
      </main>
    </div>
  )
}
