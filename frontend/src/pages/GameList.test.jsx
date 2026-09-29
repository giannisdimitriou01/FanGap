import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'

import GameList from '../pages/GameList.jsx'

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({
        items: [
          {
            id: 1,
            title: 'Hades',
            release_date: '2020-09-17',
            genres: ['Action'],
            platforms: ['PC'],
            cover_url: null,
            divergence: 4,
            critic_score: 94,
            fan_score: 98,
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        genres: ['Action'],
        platforms: ['PC'],
      }),
    })),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
})

it('renders games from the API', async () => {
  render(
    <MemoryRouter>
      <GameList />
    </MemoryRouter>,
  )
  expect(await screen.findByRole('heading', { name: 'Hades' })).toBeInTheDocument()
  expect(screen.getByText(/Gap 4/)).toBeInTheDocument()
})
