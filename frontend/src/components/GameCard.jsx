import { Link } from 'react-router-dom'

function releaseYear(releaseDate) {
  if (!releaseDate) {
    return null
  }
  return releaseDate.slice(0, 4)
}

export default function GameCard({ game }) {
  const year = releaseYear(game.release_date)

  return (
    <Link
      to={`/games/${game.id}`}
      className="block overflow-hidden rounded-xl border border-slate-800 bg-slate-900/80 shadow-sm transition hover:border-slate-600"
    >
      {game.cover_url ? (
        <img
          src={game.cover_url}
          alt=""
          className="h-40 w-full object-cover"
        />
      ) : (
        <div className="flex h-40 items-center justify-center bg-slate-800 text-3xl font-semibold text-slate-500">
          {game.title.charAt(0)}
        </div>
      )}
      <div className="space-y-3 p-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-50">{game.title}</h2>
          {year ? <p className="text-sm text-slate-400">{year}</p> : null}
        </div>
        {game.genres.length > 0 ? (
          <p className="text-sm text-slate-300">{game.genres.join(' · ')}</p>
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
        {game.divergence != null ? (
          <p className="text-sm text-amber-300">
            Gap {Number(game.divergence).toFixed(1)}
            {game.critic_score != null && game.fan_score != null
              ? ` · critics ${Number(game.critic_score).toFixed(0)} / players ${Number(game.fan_score).toFixed(0)}`
              : null}
          </p>
        ) : null}
      </div>
    </Link>
  )
}
