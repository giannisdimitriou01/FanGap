import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'

import GameDetail from './GameDetail.jsx'

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url) => {
      const path = String(url)
      if (path.includes('/ratings/history')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ items: [] }),
        }
      }
      if (path.includes('/games/by-igdb/113112')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            igdb_id: 113112,
            title: 'Hades',
            release_date: '2020-09-17',
            genres: ['Action'],
            platforms: ['PC'],
            cover_url: null,
            featured_game_id: null,
            live: {
              igdb_id: 113112,
              title: 'Hades',
              critic_score: 94,
              fan_score: 98,
              divergence: 4,
              critic_samples: 1,
              fan_samples: 1,
              scores: [],
            },
          }),
        }
      }
      return { ok: false, status: 404, json: async () => ({}) }
    }),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
})

it('renders live scores from catalog detail', async () => {
  render(
    <MemoryRouter initialEntries={['/games/igdb/113112']}>
      <Routes>
        <Route path="/games/igdb/:igdbId" element={<GameDetail />} />
      </Routes>
    </MemoryRouter>,
  )
  expect(await screen.findByRole('heading', { name: 'Hades' })).toBeInTheDocument()
  expect(screen.getByText('Critics')).toBeInTheDocument()
})

it('shows a not-found state for a missing game', async () => {
  render(
    <MemoryRouter initialEntries={['/games/igdb/999']}>
      <Routes>
        <Route path="/games/igdb/:igdbId" element={<GameDetail />} />
      </Routes>
    </MemoryRouter>,
  )
  expect(await screen.findByText('That game was not found.')).toBeInTheDocument()
})
