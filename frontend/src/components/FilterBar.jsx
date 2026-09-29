export default function FilterBar({
  q,
  genre,
  platform,
  sort,
  genres = [],
  platforms = [],
  onChange,
}) {
  return (
    <form
      className="grid gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:grid-cols-2 lg:grid-cols-4"
      onSubmit={(event) => event.preventDefault()}
    >
      <label className="block text-sm">
        <span className="mb-1 block text-slate-400">Search</span>
        <input
          type="search"
          value={q}
          onChange={(event) => onChange({ q: event.target.value })}
          placeholder="Game title"
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-slate-400">Genre</span>
        <select
          value={genre}
          onChange={(event) => onChange({ genre: event.target.value })}
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
        >
          <option value="">All genres</option>
          {genres.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-slate-400">Platform</span>
        <select
          value={platform}
          onChange={(event) => onChange({ platform: event.target.value })}
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
        >
          <option value="">All platforms</option>
          {platforms.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-slate-400">Sort</span>
        <select
          value={sort}
          onChange={(event) => onChange({ sort: event.target.value })}
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
        >
          <option value="title">Title</option>
          <option value="divergence">Most divergent</option>
        </select>
      </label>
    </form>
  )
}
