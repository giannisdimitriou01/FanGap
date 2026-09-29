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

export async function fetchFeaturedGames({ page = 1, pageSize = 20, sort = 'title', signal } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    sort,
  })
  return getJson(`/games?${params}`, { signal })
}

export async function fetchFeaturedGame(id, { signal } = {}) {
  return getJson(`/games/${id}`, { signal })
}

export async function fetchRatingHistory(id, { signal } = {}) {
  return getJson(`/games/${id}/ratings/history`, { signal })
}

export async function fetchTopDivergence({ limit = 10, signal } = {}) {
  return getJson(`/games/divergence/top?limit=${limit}`, { signal })
}
