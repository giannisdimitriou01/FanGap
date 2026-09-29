const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

async function getJson(path, { signal } = {}) {
  const response = await fetch(`${API_BASE}${path}`, { signal })
  if (response.status === 404) {
    const error = new Error('Not found')
    error.status = 404
    throw error
  }
  if (response.status === 503) {
    throw new Error('IGDB is not configured on the server.')
  }
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}

export async function searchCatalog({ q = '', page = 1, pageSize = 20, signal } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })
  if (q) {
    params.set('q', q)
  }
  return getJson(`/catalog/games?${params}`, { signal })
}

export async function fetchCatalogGame(igdbId, { signal } = {}) {
  return getJson(`/catalog/games/${igdbId}`, { signal })
}

export async function fetchCatalogLive(igdbId, { signal } = {}) {
  return getJson(`/catalog/games/${igdbId}/live`, { signal })
}

export async function fetchCatalogDetail(igdbId, { signal } = {}) {
  return getJson(`/games/by-igdb/${igdbId}`, { signal })
}
