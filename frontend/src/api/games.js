const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export async function fetchGames({ page = 1, pageSize = 20, signal } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })
  const response = await fetch(`${API_BASE}/games?${params}`, { signal })
  if (!response.ok) {
    throw new Error(`Failed to load games (${response.status})`)
  }
  return response.json()
}
