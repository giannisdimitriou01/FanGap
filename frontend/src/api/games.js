const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

async function getJson(path, { signal } = {}) {
  const response = await fetch(`${API_BASE}${path}`, { signal })
  if (response.status === 404) {
    const error = new Error('Not found')
    error.status = 404
    throw error
  }
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}

export async function fetchGames({
  page = 1,
  pageSize = 20,
  q = '',
  genre = '',
  platform = '',
  sort = 'title',
  signal,
} = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    sort,
  })
  if (q) params.set('q', q)
  if (genre) params.set('genre', genre)
  if (platform) params.set('platform', platform)
  return getJson(`/games?${params}`, { signal })
}

export async function fetchGame(id, { signal } = {}) {
  return getJson(`/games/${id}`, { signal })
}

export async function fetchRatingHistory(id, { signal } = {}) {
  return getJson(`/games/${id}/ratings/history`, { signal })
}

export async function fetchLatestRatings(id, { signal } = {}) {
  return getJson(`/games/${id}/ratings`, { signal })
}

export async function fetchGameDivergence(id, { signal } = {}) {
  return getJson(`/games/${id}/divergence`, { signal })
}

export async function fetchTopDivergence({ limit = 20, signal } = {}) {
  return getJson(`/games/divergence/top?limit=${limit}`, { signal })
}
