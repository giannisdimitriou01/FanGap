const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export async function fetchLiveLeaderboard({ limit = 50, signal } = {}) {
  const response = await fetch(`${API_BASE}/leaderboard/live?limit=${limit}`, { signal })
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}
