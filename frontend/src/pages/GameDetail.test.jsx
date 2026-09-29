import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'

import GameDetail from './GameDetail.jsx'

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url) => {
      const path = String(url)
      if (path.endsWith('/ratings/history')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ items: [] }),
        }
      }
      if (path.includes('/games/1')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            id: 1,
            title: 'Hades',
            release_date: '2020-09-17',
            genres: ['Action'],
            platforms: ['PC'],
            cover_url: null,
            critic_score: 94,
            fan_score: 98,
            divergence: 4,
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

it('renders a game loaded from GET /games/:id', async () => {
  render(
    <MemoryRouter initialEntries={['/games/1']}>
      <Routes>
        <Route path="/games/:gameId" element={<GameDetail />} />
      </Routes>
    </MemoryRouter>,
  )
  expect(await screen.findByRole('heading', { name: 'Hades' })).toBeInTheDocument()
  expect(screen.getByText('Critics')).toBeInTheDocument()
})

it('shows a not-found state for a missing game', async () => {
  render(
    <MemoryRouter initialEntries={['/games/999']}>
      <Routes>
        <Route path="/games/:gameId" element={<GameDetail />} />
      </Routes>
    </MemoryRouter>,
  )
  expect(await screen.findByText('That game was not found.')).toBeInTheDocument()
})
